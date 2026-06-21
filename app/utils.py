import os
import logging
import resend
from resend.exceptions import ResendError

logger = logging.getLogger(__name__)


def remove_temp_file(path: str) -> None:
    if os.path.exists(path):
        os.remove(path)


def send_email(
    subject: str, body: str, to: list | None = None, bcc: list | None = None
) -> None:
    params = {
        "from": "noreply@opvlad.dev",
        "to": to,
        "bcc": bcc,
        "subject": subject,
        "html": body,
    }

    try:
        email = resend.Emails.send(params)
        logger.info(f"EMAIL_SENT | id={email['id']}")
    except ResendError as e:
        logger.error(f"EMAIL_ERROR | {e}", exc_info=True)
        raise
    except Exception:
        raise
