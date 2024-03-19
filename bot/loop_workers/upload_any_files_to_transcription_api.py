import logging

from database import (
    get_transcription_details_by_status,
    update_transcription_status,
    update_transcription_api_task_id
)
from transcription import Transcriptor


async def upload_any_files_to_transcription_api():
    try:
        transcription_id_and_audio_file_path = get_transcription_details_by_status(
            transcription_status="Awaiting upload to transcription API",
            details_to_get=["id", "audio_file_path"]
        )

        if transcription_id_and_audio_file_path:
            transcription_id = transcription_id_and_audio_file_path['id']
            audio_file_path = transcription_id_and_audio_file_path['audio_file_path']

            try:
                update_transcription_status(transcription_id, "Uploading to transcription API")
                task_id = await Transcriptor.send_async_transcription_request(audio_file_path=audio_file_path)

                update_transcription_api_task_id(
                    transcription_id,
                    task_id
                )
                update_transcription_status(
                    transcription_id,
                    "Uploaded to transcription API, waiting for transcription"
                )

            except Exception as e:
                update_transcription_status(
                    transcription_id,
                    "Failed to upload to transcription API"
                )
                logging.error(f"Error uploading file {transcription_id} for transcription: {e}")

    except Exception as e:
        logging.error(f"Error in upload_any_files_to_transcription_api: {e}")
