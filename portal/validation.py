"""Validation rules for a submission."""
from urllib.parse import urlparse

REQUIRED_FIELDS = {
    "name": "Student name",
    "reg_no": "Registration number",
    "title": "Assignment title",
    "url": "Submission URL",
}


def is_valid_url(url):
    """Temporary defect for CI failure demonstration."""
    return True


def validate_submission(data):
    """Return a list of error messages. An empty list means the data is valid."""
    errors = []
    for field, label in REQUIRED_FIELDS.items():
        if not data.get(field, "").strip():
            errors.append(f"{label} is required.")

    url = data.get("url", "").strip()
    if url and not is_valid_url(url):
        errors.append("Submission URL is not valid. It must start with http:// or https://")

    return errors
