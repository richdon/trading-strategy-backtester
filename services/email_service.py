from flask_mail import Mail, Message
from flask import current_app
from typing import Optional


class EmailService:
    def __init__(self, mail: Mail):
        self.mail = mail

    def send_trading_signal(
            self,
            to_email: str,
            signal_type: str,
            asset: str,
            amount: float,
            price: float,
            strategy_name: Optional[str] = None
    ):
        """
        Send trading signal email to user
        """
        subject = f"Trading Signal Alert: {signal_type} {asset}"

        # Create a more professional email template
        body = f"""
        Trading Signal Detected
        ----------------------

        Strategy: {strategy_name or 'Custom Strategy'}
        Signal Type: {signal_type}
        Asset: {asset}
        Amount: {amount:.8f}
        Current Price: ${price:,.2f}
        Total Value: ${(amount * price):,.2f}

        Please review this signal and make your trading decision.

        Note: This is an automated message. Do not reply to this email.
        """

        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )

        self.mail.send(msg)
