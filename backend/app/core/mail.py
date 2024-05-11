from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.background import BackgroundTasks

from app.core.config import settings


class Mail:
    def __init__(
        self,
        mail_username=settings.mail.username,
        mail_password=settings.mail.password,
        mail_from=settings.mail.from_email,
        mail_port=settings.mail.port,
        mail_sever=settings.mail.server,
        mail_server_name=settings.mail.from_name,
        mail_ssl_tls=settings.mail.ssl_tls,
        mail_starttls=settings.mail.starttls,
        use_credentials=settings.mail.use_credentials,
        mail_debug=settings.mail.debug,
        template_folder=Path(__file__).parent.parent / "templates/mail",
    ):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=mail_username,
            MAIL_PASSWORD=mail_password,
            MAIL_FROM=mail_from,
            MAIL_PORT=mail_port,
            MAIL_SERVER=mail_sever,
            MAIL_FROM_NAME=mail_server_name,
            MAIL_SSL_TLS=mail_ssl_tls,
            USE_CREDENTIALS=use_credentials,
            MAIL_STARTTLS=mail_starttls,
            MAIL_DEBUG=mail_debug,
            TEMPLATE_FOLDER=template_folder,
        )

    async def send_email_async(
        self, subject: str, email_to: str, body: str, template_body: dict
    ):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            template_body=template_body,
            subtype=MessageType.html,
        )
        fm = FastMail(self.conf)
        await fm.send_message(message, template_name="email.html")

    def send_email_background(
        self,
        background_tasks: BackgroundTasks,
        subject: str,
        email_to: str,
        body: str,
        template_body: dict,
        template_name: str = "email.html",
    ):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            template_body=template_body,
            subtype=MessageType.html,
        )
        fm = FastMail(self.conf)
        background_tasks.add_task(fm.send_message, message, template_name=template_name)


mail = Mail()
