import logging

from database import (
    get_details_for_any_transcription_with_given_status,
    update_transcription_details_by_id
)
from transcription import Transcriptor


async def upload_any_files_to_transcription_api():
    transcription_id_and_audio_file_path = get_details_for_any_transcription_with_given_status(
        transcription_status="Awaiting upload to transcription API",
        details_to_get=["id", "audio_file_path"]
    )

    if transcription_id_and_audio_file_path:
        transcription_id = transcription_id_and_audio_file_path['id']
        audio_file_path = transcription_id_and_audio_file_path['audio_file_path']

        try:
            update_transcription_details_by_id(
                transcription_id,
                {'status': "Uploading to transcription API"}
            )
            task_id = await Transcriptor.send_async_transcription_request(audio_file_path=audio_file_path)

            update_transcription_details_by_id(
                transcription_id,
                {
                    'transcription_api_task_id': task_id,
                    'status': "Uploaded to transcription API, waiting for transcription"
                }
            )

            logging.info(f"File {transcription_id} uploaded to transcription API")

        except Exception as e:
            update_transcription_details_by_id(
                transcription_id,
                {'status': "Failed to upload to transcription API"}
            )

            logging.error(f"Error uploading file {transcription_id} for transcription: {e}")
