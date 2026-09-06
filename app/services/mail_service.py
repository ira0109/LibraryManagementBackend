import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MailService")

class MailService:
    @staticmethod
    def send_automated_email(recipient: str, subject: str, body: str):
        logger.info("================ [AUTOMATED EMAIL SYSTEM] ================")
        logger.info("To: %s", recipient)
        logger.info("Subject: %s", subject)
        logger.info("Body:\n%s", body)
        logger.info("============================================================")