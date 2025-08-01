import csv
import os
from dotenv import load_dotenv
from openai import OpenAI
from email_client import GmailClient

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gmail = GmailClient()

def generate_rejection_email(first_name: str, feedback: str) -> str:
    prompt = (
        f"Write a short, professional, and warm rejection email to an applicant named {first_name} "
        f"for a university student club, based on the following bullet point feedback:\n- {feedback}\n\n"
        "Keep the tone kind and encouraging. Do NOT include a subject line.\n"
        "Start with 'Dear {name},'. Keep it concise — no more than 3 short paragraphs.\n"
        "End with a warm invitation to apply again next semester.\n"
        "Sign off as 'DsCubed Recruitment Team'. Please structure the email as a properly formatted email in HTML and remove the HTML tag."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional and kind recruiter at a student club."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()

with open("rejected_interview.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]
        feedback = row.get("Exec Comments", "").strip()

        if not feedback:
            print(f"⚠️ Skipping {first_name} {last_name} ({email}) — no feedback provided.")
            continue


        print(f"✏️ Generating rejection email for {first_name} {last_name}...")
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            body = generate_rejection_email(first_name, feedback)
            print("\n Preview email:\n")
            print(body)
            user_input = input("\nDo you want to sent this email? (y=yes / r= regenerate / s = skip) ").strip().lower()

            if user_input == "y":
                subject = "Application to DsCubed"
                gmail.send_email(
                    sender="recruitment@dscubed.org.au",
                    recipient=email,
                    subject=subject,
                    body=body
                )
                print(f"✅ Email sent to {first_name} {last_name}({email})\n")
                break

            elif user_input == "r":
                attempts += 1
                print("🔁 Regenerating...\n")
            elif user_input == "s":
                print(f"⏭️ Skipped {first_name} {last_name} ({email})\n")
                break
            else:
                print("❌ Invalid input. Please enter 'y', 'r', or 's'.")

