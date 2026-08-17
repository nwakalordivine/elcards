import resend
from elcards_backend.settings import settings, BASE_DIR
import random
import hashlib
import jwt
from datetime import datetime, timezone, timedelta


async def send_email(to: str, subject: str, code: int) -> bool:
    resend.api_key = settings.resend_apikey

    params: resend.Emails.SendParams = {
        "from": f"Elcard <{settings.my_email}>",
        "to": [to],
        "subject": subject,
        "html": f"<!DOCTYPE html><html><body><h1>Enter this code to reset your password.</h1>\n<p>{code}</p>\n<p>this code will expire in {settings.reset_code_timer} minutes.</p></body></html>"
    }
    try:
        email: resend.Emails.SendResponse = await resend.Emails.send_async(params)
    except Exception as e:
        print(f"[email_error]: {e}")
        return False
    else:
        print(f"[email sent]: {email}")

    return True


def get_random_code(length: int) -> str:
    return str(random.randint(10 ** (length - 1), (10 ** length) - 1))


def get_hash(code: str):
    return hashlib.sha256(code.encode()).hexdigest()




def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes)
    }
    return jwt.encode(payload, settings.secret, algorithm=settings.algorithm)


if __name__ == "__main__":
    # random 4 digit code
    print(get_random_code(4))

