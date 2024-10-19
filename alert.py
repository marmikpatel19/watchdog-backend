import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("TWILIO_AUTH_TOKEN"))
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

weapon = "gun";

message = client.messages.create(
    body=f'ALERT: Active {weapon} reported in the building. Please find the nearest safe area and secure yourself immediately. Avoid open areas and remain silent. Wait for further instructions from authorities.',
    from_= os.environ.get('TWILIO_PHONE'),
    to=os.environ.get('PERSONAL_PHONE'),
)

print(message.body)