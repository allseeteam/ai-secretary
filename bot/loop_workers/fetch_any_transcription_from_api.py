import logging

from database import (
    get_transcription_details_by_status,
    update_transcription_status,
    add_transcription_text_to_db
)
from transcription import Transcriptor


async def fetch_any_transcription_from_api():
    try:
        transcription_id_and_api_task_id = get_transcription_details_by_status(
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
                    update_transcription_status(transcription_id, "Transcribed")

                elif status == "failed":
                    update_transcription_status(transcription_id, "Transcription API internal error")

            except Exception as e:
                logging.error(f"Error processing transcription result for file {transcription_id}: {e}")
                update_transcription_status(transcription_id, "Transcription loop error")

    except Exception as e:
        logging.error(f"Error in fetch_any_transcription_from_api: {e}")
