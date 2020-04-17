import os
from requests import Response, post


class Mailgun:
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    FROM_EMAIL = os.environ.get("FROM_EMAIL")
    FROM_TITLE = "REST API - FLASK"

    @classmethod
    def send_email(cls, email, subject, text, html):
        return post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html
            },
        )
