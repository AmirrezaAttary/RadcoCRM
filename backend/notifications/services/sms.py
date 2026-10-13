from django.conf import settings

from sms_ir import SmsIr


class SmsService:

    def __init__(self):
        self.client = SmsIr(
            settings.SMS_IR_API_KEY,
            settings.SMS_IR_LINE_NUMBER,
        )

    def send(self, number, message):
        return self.client.send_sms(
            number,
            message,
            settings.SMS_IR_LINE_NUMBER,
        )