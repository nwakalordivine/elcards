import resend
from elcards_backend.settings import settings, BASE_DIR
import random


async def send_email(to: str, subject: str, code: int) -> bool:
    resend.api_key = settings.resend_apikey

    params: resend.Emails.SendParams = {
        "from": f"Elcard <{settings.my_email}>",
        "to": [to],
        "subject": subject,
        "html": f"<!DOCTYPE html><html><body><h1>Enter this code to reset your password.</h1>\n<p>{code}</p>\n<p>this code will expire in {settings.reset_code_timer} minutes.</p></body></html>"
    }

    email: resend.Emails.SendResponse = await resend.Emails.send_async(params)
    print(f"[email sent]: {email}")
    return True


def get_random_code(length: int) -> str:
    return str(random.randint(10 ** (length - 1), (10 ** length) - 1))


if __name__ == "__main__":
    # random 4 digit code
    print(get_random_code(4))