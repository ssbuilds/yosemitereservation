import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime

logger = logging.getLogger(__name__)

def mask_email(email: str) -> str:
    """
    Mask an email address for privacy (e.g., jo***@example.com)
    """
    if not email or '@' not in email:
        return email

    username, domain = email.split('@')
    if len(username) <= 2:
        masked_username = username[0] + '*' * (len(username) - 1)
    else:
        masked_username = username[0:2] + '*' * (len(username) - 2)

    return f"{masked_username}@{domain}"

def send_notification_email(to_email: str, month: str, available_dates: list[str] | None = None) -> bool:
    """
    Send an email notification using SendGrid when entry reservation requirements are detected.
    """
    try:
        # Only send email if we have specific dates
        if not available_dates:
            logger.info(f"No specific dates provided for {month}, skipping email notification")
            return False
            
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

        # Remove duplicates while preserving order
        seen = set()
        unique_dates = []
        for date in available_dates:
            if date not in seen:
                seen.add(date)
                unique_dates.append(date)
        available_dates = unique_dates

        # Create the email content
        subject = f"Important: Entry Reservation Requirements at Yosemite for {month}"

        # Simple, clean email template
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2c5530; font-size: 24px; margin-bottom: 20px;">
                Entry Reservation Requirements Detected
            </h1>

            <p style="font-size: 16px; margin-bottom: 20px;">
                A reservation is required to drive into Yosemite 24 hours per day for visitors arriving during these dates in {month}:
            </p>

            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <ul style="list-style-type: none; padding: 0; margin: 0;">
                    {''.join(f"<li style='margin: 10px 0; padding-left: 20px;'>• {date}</li>" for date in available_dates)}
                </ul>
            </div>

            <p style="margin: 20px 0;">
                <a href="https://www.nps.gov/yose/planyourvisit/reservations.htm" 
                   style="color: #2c5530; text-decoration: underline;">
                    View full details and make reservations on the Yosemite website
                </a>
            </p>

            <p style="color: #666; font-size: 14px; font-style: italic;">
                Note: Requirements may change. Always verify information on the official website.
            </p>
        </div>
        """

        message = Mail(
            from_email=Email(os.environ.get('SENDGRID_VERIFIED_SENDER')),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        response = sg.send(message)
        if response.status_code == 202:
            logger.info(f"Successfully sent notification email to {mask_email(to_email)}")
            return True
        else:
            logger.error(f"Failed to send email. Status code: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error sending notification email: {str(e)}")
        return False