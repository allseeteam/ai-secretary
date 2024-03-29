import logging

from telegram import File
from telegram.ext import Application

from database import (
    get_details_for_any_transcription_with_given_status,
    update_transcription_details_by_id,
)


async def extract_any_transcription_file_path_from_bot_server(application: Application) -> None:
    transcription_id_file_id_and_file_type = get_details_for_any_transcription_with_given_status(
        transcription_status="Awaiting to filepath extraction",
        details_to_get=["id", "uploaded_file_id", "uploaded_file_type"]
    )

    if transcription_id_file_id_and_file_type:
        transcription_id = transcription_id_file_id_and_file_type['id']
        uploaded_file_id = transcription_id_file_id_and_file_type['uploaded_file_id']
        uploaded_file_type = transcription_id_file_id_and_file_type['uploaded_file_type']

        try:
            file_for_transcription: File = await application.bot.get_file(uploaded_file_id)
            file_for_transcription_file_path = file_for_transcription.file_path

            if uploaded_file_type == "Video":
                update_transcription_details_by_id(
                    transcription_id,
                    {
                        'video_file_path': file_for_transcription_file_path,
                        'status': "Awaiting to audio extraction"
                    }
                )
            elif uploaded_file_type == "Audio":
                update_transcription_details_by_id(
                    transcription_id,
                    {
                        'audio_file_path': file_for_transcription_file_path,
                        'status': "Awaiting upload to transcription API"
                    }
                )
            else:
                raise Exception(f"Unknown file type {uploaded_file_type} for transcription {transcription_id}")

            logging.info(f"File {transcription_id} filepath extracted from bot server")

        except Exception as e:
            update_transcription_details_by_id(
                transcription_id,
                {'status': "Failed to save transcription file path"}
            )

            logging.error(f"Error saving {transcription_id} file path: {e}")
