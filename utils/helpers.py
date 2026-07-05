"""TruthGuard AI — Helper utilities."""

import uuid
import os

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',  # images
    'mp4', 'avi', 'mov', 'mkv', 'webm',           # videos
    'pdf', 'doc', 'docx',                          # documents
}


def allowed_file(filename: str) -> bool:
    """Check if uploaded file extension is permitted."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_report_id() -> str:
    """Generate a short unique report identifier."""
    return 'TG-' + str(uuid.uuid4())[:8].upper()


def format_result(record: dict) -> dict:
    """Format a scan record for clean API response."""
    return {
        'id':         record.get('id'),
        'result':     record.get('result'),
        'confidence': record.get('confidence'),
        'timestamp':  record.get('timestamp'),
        'details':    record.get('details', {}),
        'filename':   record.get('filename'),
        'type':       record.get('type'),
    }


def human_filesize(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
