from .callback_query import handle_callback_query
from .file_upload import handle_audio
from .start import handle_start
from .text import handle_text

__all__ = [
    'handle_start',
    'handle_callback_query',
    'handle_text',
    'handle_audio'
]
