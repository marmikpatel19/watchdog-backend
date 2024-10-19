from etext import send_mms_via_email
import os
from dotenv import load_dotenv

load_dotenv()

file_path = "temp-photos/knife.png"

mime_maintype = "image"
mime_subtype = "png"

phone_number = os.getenv("SMTPLIB_PERSONAL_PHONE")
message = "hello world!"
provider = "AT&T"

sender_credentials = (os.getenv("SMTPLIB_SENDER_EMAIL"), os.getenv("SMTPLIB_SENDER_CREDENTIALS"))

send_mms_via_email(
    phone_number,
    message,
    file_path,
    mime_maintype,
    mime_subtype,
    provider,
    sender_credentials,
)
