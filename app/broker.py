import logging
import resend
from resend.exceptions import ResendError
from celery import Celery

from app.config.settings import settings


app = Celery("broker", broker=settings.redis_url, backend=settings.redis_url)
logger = logging.getLogger(__name__)
resend.api_key = settings.resend_api_key


@app.task(
    autoretry_for=(ResendError,),
    max_retries=3,
    default_retry_delay=60,
)
def send_email(
    subject: str, body: str, to: list | None = None, bcc: list | None = None
) -> None:
    if not to and not bcc:
        raise ValueError("to or bcc is required")

    params = {
        "from": settings.email_sender,
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
    except Exception as e:
        logger.error(f"UNEXPECTED_ERROR | {e}", exc_info=True)
        raise
