"""Sends the first round generic rejection email"""

import csv
from email_client import GmailClient

gmail = GmailClient()

with open("rejected_initial_filtration.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]

        subject = f"Application to DsCubed"

        body = f"""
        <p>Dear {first_name},</p>

        <p>Thank you for taking the time to apply to the <strong>Data Science Student Society</strong>.</p>

        <p>We truly appreciate the effort you put into your application. After reviewing many impressive submissions, we regret to inform you that we won’t be moving forward with your application at this time. We value your interest and encourage you to apply again — we’d love to see you stay engaged with the club.</p>

        <p>Wishing you all the best in your future endeavors.</p>

        <p>Warm regards,</p>

        <p>DsCubed Recruitment Team</p>
        """

        gmail.send_email(
            sender="recruitment@dscubed.org.au",
            recipient=email,
            subject=subject,
            body=body
        )