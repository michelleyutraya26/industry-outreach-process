"""Sends interview schedules"""

import csv
from email_client import GmailClient

gmail = GmailClient()

with open("accepted_interview.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]

        subject = "You're invited to the next stage – DsCubed Interview Invitation 🎉"

        body = f"""
        <p>Dear {first_name},</p>

        <p>We’re excited to inform you that you’ve been accepted to join the <strong>Data Science Student Society</strong>! 🎉</p>

        <p>Congratulations and welcome aboard — we were impressed by your application and can’t wait to have you on the team. We’ll be in touch soon with further details about your onboarding and upcoming events. In the meantime, if you have any questions, feel free to reach out.</p>

        <p>Warm regards,<br>
        <strong>DsCubed Recruitment Team</strong></p>
        """

        gmail.send_email(
            sender="recruitment@dscubed.org.au",
            recipient=email,
            subject=subject,
            body=body
        )

