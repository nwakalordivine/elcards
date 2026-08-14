import resend
from elcards_backend.settings import settings, BASE_DIR



def send_email(to: str, subject: str) -> None:
    resend.api_key = settings.resend_apikey

    params: resend.Emails.SendParams = {
        "from": f"Elcard <{settings.my_email}>",
        "to": [to],
        "subject": subject
    }


    email = resend.Emails.send(params)
    print(f"[email sent]: {email}")
    