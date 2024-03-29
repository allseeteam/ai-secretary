import logging

from database import (
    get_details_for_any_transcription_with_given_status,
    update_transcription_details_by_id,
    add_transcription_text_to_db
)
from transcription import Transcriptor


async def fetch_any_transcription_from_api():
    transcription_id_and_api_task_id = get_details_for_any_transcription_with_given_status(
        transcription_status="Uploaded to transcription API, waiting for transcription",
        details_to_get=["id", "transcription_api_task_id"]
    )

    if transcription_id_and_api_task_id:
        transcription_id = transcription_id_and_api_task_id['id']
        transcription_api_task_id = transcription_id_and_api_task_id['transcription_api_task_id']

        try:
            status = await Transcriptor.get_async_transcription_status(
                operation_id=transcription_api_task_id
            )

            if status == "completed":
                transcription_result = await Transcriptor.get_async_transcription_result(
                    operation_id=transcription_api_task_id
                )
                add_transcription_text_to_db(transcription_id, transcription_result)
                update_transcription_details_by_id(
                    transcription_id,
                    {'status': "Transcribed"}
                )

                logging.info(f"File {transcription_id} transcribed")

            elif status == "failed":
                update_transcription_details_by_id(
                    transcription_id,
                    {'status': "Transcription API internal error"}
                )

                logging.info(f"File {transcription_id} failed to transcribe")

        except Exception as e:
            update_transcription_details_by_id(
                transcription_id,
                {'status': "Transcription loop error"}
            )

            logging.error(f"Error processing transcription result for file {transcription_id}: {e}")
