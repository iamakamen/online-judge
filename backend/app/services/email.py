import os

import httpx
from dotenv import load_dotenv

load_dotenv()

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class EmailDeliveryError(Exception):
    """Raised when an email cannot be delivered through Brevo."""


def send_otp_email(
    *,
    recipient_email: str,
    otp: str,
) -> None:
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("BREVO_SENDER_EMAIL")
    sender_name = os.getenv("BREVO_SENDER_NAME")

    if not api_key:
        raise EmailDeliveryError("Brevo API key is not configured")

    if not sender_email:
        raise EmailDeliveryError("Brevo sender email is not configured")

    if not sender_name:
        raise EmailDeliveryError("Brevo sender name is not configured")

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": recipient_email,
            }
        ],
        "subject": "Online Judge email verification",
        "textContent": (
            "Your Online Judge verification code is "
            f"{otp}.\n\n"
            "This code expires in 5 minutes."
        ),
    }

    try:
        response = httpx.post(
            BREVO_API_URL,
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json=payload,
            timeout=10.0,
        )
    except httpx.HTTPError as exc:
        raise EmailDeliveryError(
            "Unable to connect to email delivery service"
        ) from exc

    if response.is_error:
        raise EmailDeliveryError(
            f"Email delivery failed with status {response.status_code}"
        )
