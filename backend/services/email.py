from settings import MailSettings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
import traceback

OTP_TEMPLATE = "otp_template.html"

settings = MailSettings()
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER="./templates",
)

async def send_email_async(subject: str, email_to: str, otp: str) -> bool:
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body={"otp_code": otp},
        subtype="html",
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name=OTP_TEMPLATE)
        return True
    except Exception as e:
        traceback.print_exc()
        return False
