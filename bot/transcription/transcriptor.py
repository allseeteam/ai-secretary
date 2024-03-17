import asyncio
from typing import Dict, Any, Callable
from aiohttp import ClientSession, FormData
from pydantic_settings import BaseSettings
from functools import wraps


class TranscriptorSettings(BaseSettings):
    transcription_api_base_url: str

    class Config:
        env_file = 'env/.env.transcriptor'


transcriptor_settings = TranscriptorSettings()


def with_transcriptor_settings(transcriptor_func: Callable) -> Callable:
    @wraps(transcriptor_func)
    def call_with_settings(*args, **kwargs):
        transcriptor_func_result: Any = transcriptor_func(transcriptor_settings, *args, **kwargs)
        return transcriptor_func_result

    return call_with_settings


class Transcriptor(object):
    @staticmethod
    @with_transcriptor_settings
    async def send_async_transcription_request(
            settings: TranscriptorSettings,
            audio_file_path: str
    ) -> str:
        transcription_request_url = f"{settings.transcription_api_base_url}/transcribe/"

        transcription_form_data = FormData()
        transcription_form_data.add_field(
            'file',
            open(audio_file_path, 'rb'),
            filename=audio_file_path.split('/')[-1],
            content_type='audio/mpeg'
        )

        async with ClientSession() as session:
            async with session.post(transcription_request_url, data=transcription_form_data) as response:
                if response.status == 200:
                    response_json = await response.json()
                    transcription_task_id = response_json['task_id']
                    return transcription_task_id
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to send transcription request: {response.status} {error_text}")

    @staticmethod
    @with_transcriptor_settings
    async def get_async_transcription_status(
            settings: TranscriptorSettings,
            operation_id: str
    ) -> str:
        transcription_status_request_url = f"{settings.transcription_api_base_url}/transcribe/status/{operation_id}"

        async with ClientSession() as session:
            async with session.get(transcription_status_request_url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    transcription_status = response_json['status']
                    return transcription_status
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get transcription status: {response.status} {error_text}")

    @staticmethod
    @with_transcriptor_settings
    async def get_async_transcription_result(
            settings: TranscriptorSettings,
            operation_id: str
    ) -> str:
        def get_transcription_text_from_json(transcript_json: Dict[str, Any]) -> str:
            transcript = ''
            last_speaker = 'Участник не определен'

            for segment in transcript_json['segments']:
                current_speaker: str = segment.get('speaker', 'Участник не определен').replace('SPEAKER_', 'Участник ')

                if current_speaker == last_speaker:
                    transcript += f" {segment['text']}"
                else:
                    if len(transcript) > 0:
                        transcript += "\n"
                    transcript += f"{current_speaker}: {segment['text']}"

                last_speaker = current_speaker

            return transcript

        transcription_result_request_url = f"{settings.transcription_api_base_url}/transcribe/result/{operation_id}"

        async with ClientSession() as session:
            async with session.get(transcription_result_request_url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    transcription_result_json = response_json['result']
                    transcription_result = get_transcription_text_from_json(transcription_result_json)
                    return transcription_result
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get transcription result: {response.status} {error_text}")
