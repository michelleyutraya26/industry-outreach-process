import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to check if a URL is allowed by robots.txt
def is_allowed_by_robots(url: str, user_agent: str = "MyScraperBot") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        # If robots.txt cannot be fetched, default to allow scraping
        return True

# Extract visible text from a website
def scrape_website_text(url: str) -> str:
    if not is_allowed_by_robots(url):
        return f"Scraping not allowed by robots.txt for {url}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts and style tags
        for script_or_style in soup(["script", "style", "noscript"]):
            script_or_style.decompose()

        # Extract visible text
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split()[:300])  # Limit to ~300 words
    except Exception as e:
        return f"Failed to fetch website content: {e}"


# Updated function using scraped website content
def generate_personalised_with_website(company: str, website_url: str, club_info: str) -> str:
    website_info = scrape_website_text(website_url)

    # print(f"Scraped content from {website_url}:\n{website_info[:500]}...\n")  # Print first 500 chars for debugging

    if website_info.startswith("Failed to fetch"):
        print("Failed to fetch website content. Skipping message generation.\n")
        return f"(Error fetching content from {website_url}. Skipping message generation.)"

    prompt = (
        f"Using the company name '{company}' and the following extracted website content:\n\n{website_info}\n\n"
        f"Here is some information about our club:\n{club_info}\n\n"
        "Write exactly two sentences for a sponsorship reach-out email section that is specific and relevant to the company. "
        "Keep the tone professional and engaging, suitable for an initial outreach. Do not exceed two sentences."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional industry outreach person at a student club."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return (response.choices[0].message.content or "").strip()


def generate_personalised_with_string(company: str, company_info: str, club_info: str) -> str:
    prompt = (
        f"Using the company name '{company}' and must use the following information about the company:\n{company_info}\n\n"
        f"Here is some information about our club:\n{club_info}\n\n"
        "Write exactly two sentences for a sponsorship reach-out email section that is specific and relevant to the company. "
        "Keep the tone professional and engaging, suitable for an initial outreach. Do not exceed two sentences. Please don't include cookies in the output."
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

    return (response.choices[0].message.content or "").strip()


# Testing the functions
if __name__ == "__main__":
    company = "Heidi Health"
    website_link = "https://www.heidihealth.com/au/about-us/company"
    company_info = (
        "DSCubed recently partnered with Heidi Health at our recent Career Compass event. "
        "We really valued the insights shared by Jane and John on our STEM panel and would love to continue our collaboration."
    )
    club_info = (
        "We are DSCubed, a student-run club at the University of Melbourne focused on connecting students with real-world tech innovation. "
        "Our mission is to empower the next generation of data scientists, software engineers, and product leaders through industry events, mentorship programs, and hands-on projects."
    )
    print("Choose input method:")
    print("[1] Use company info string")
    print("[2] Scrape from website")
    choice = input("Enter your choice (1 or 2): ").strip()

    while True:
        if choice == "1":
            output = generate_personalised_with_string(company, company_info, club_info)
            print("\nGenerated message:")
            print(output)

            user_input = input("\nPress [r] to regenerate, [q] to quit, or any other key to accept: ").strip().lower()
            if user_input == "r":
                continue
            elif user_input == "q":
                break
            else:
                print("\nMessage accepted.")
                break


        elif choice == "2":
            scraped_content = scrape_website_text(website_link)
            if scraped_content.startswith("Failed to fetch"):
                print(scraped_content)
                break

            # Step 1: generate the first message immediately
            output = generate_personalised_with_website(company, website_link, club_info)
            print("\nGenerated message:")
            print(output)

            # Step 2: ask if the user wants to regenerate
            wants_to_regenerate = input("\nDo you want to regenerate? (y/n): ").strip().lower()
            if wants_to_regenerate != "y":
                print("\nMessage accepted.")
                break

            # Step 3: show scraped content and ask if it looks good
            print("\n--- Scraped Website Content Preview (First ~300 words) ---")
            print(scraped_content)
            print("-----------------------------------------------------------\n")
            satisfied = input("Are you happy with the scraped content? (y/n): ").strip().lower()

            if satisfied == "y":
                while True:
                    output = generate_personalised_with_website(company, website_link, club_info)
                    print("\nRegenerated message:")
                    print(output)
                    user_input = input(
                        "\nPress [r] to regenerate again, [q] to quit, or any other key to accept: ").strip().lower()
                    if user_input == "r":
                        continue
                    elif user_input == "q":
                        break
                    else:
                        print("\nMessage accepted.")
                        break
                break

            else:
                print("\nUnderstood. Please copy-paste relevant company info from the website.")
                user_input_text = input("\nPaste custom company info here:\n")
                output = generate_personalised_with_string(company, user_input_text, club_info)
                print("\nGenerated message based on your input:")
                print(output)
                break

        else:
            print("Invalid choice. Please enter 1 or 2.")
            break