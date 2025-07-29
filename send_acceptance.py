"""Sends interview schedules"""

import csv
from email_client import GmailClient

gmail = GmailClient()


with open("accepted_initial_filtration.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]

        subject = "You're invited to the next stage – DsCubed Interview Invitation 🎉"

        body = f"""
        <p>Dear {first_name},</p>
        
        <p>Congratulations! After reviewing your application, we’d love to invite you to the next stage of recruitment for the <strong>Data Science Student Society</strong>.</p>
        <p>This will be a face-to-face interview to get to know you better and learn more about your motivations. Please schedule a time that works best for you by filling out the following form: 👉 <a href="#">[Insert link here]</a> </p>
        
        <p>If you have any questions, feel free to reach out.</p>
        
        <p>Looking forward to meeting you!</p>
        
        <p>Warm regards,<br>
        <strong>DsCubed Recruitment Team</strong></p>
        """

        gmail.send_email(
            sender="recruitment@dscubed.org.au",
            recipient=email,
            subject=subject,
            body=body
        )
