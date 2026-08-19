from smtplib import SMTP
from email.message import EmailMessage
from elcards_backend.settings import settings, BASE_DIR
import random
import hashlib
import jwt
from datetime import datetime, timezone, timedelta



def send_email(to: str, subject: str, message: str, sender: str = settings.sender_email):
    # Create message
    msg = EmailMessage()
    msg["Subject"] = subject,
    msg["From"] = sender,
    msg["To"] = to

    msg.set_content(message)

    try:
        with SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.sender_email, settings.sender_app_password)
            server.send_message(msg)
            print("[email sent]: email sent successfully.")
    except Exception as e:
        print(f"[Email Failed]: {e}")




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

