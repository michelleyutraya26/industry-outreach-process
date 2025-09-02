import os
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Updated function using scraped website content
def generate_personalised_with_website(company: str, website_content: str, club_info: str) -> str:
    prompt = (
        f"Using the company name '{company}' and the following extracted website content:\n\n{website_content}\n\n"
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
        f"Using the company name '{company}' and must use company info:\n{company_info}\n\n"
        f"Here is our student club info:\n{club_info}\n\n"
        "Write exactly two sentences for a sponsorship reach-out email section that is specific and relevant to the company."
        "Professional and engaging tone, suitable for an initial outreach. Do not exceed two sentences."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional and kind recruiter at a student club."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return (response.choices[0].message.content or "").strip()

# Main function to run the personalised message generation
def run_personalised_message(company: str, website_link: str, company_info: str):
    club_info = (
        "We are DSCubed, a student-run club at the University of Melbourne focused on connecting students with real-world tech innovation. "
        "Our mission is to empower the next generation of data scientists, software engineers, and product leaders through industry events, mentorship programs, and hands-on projects."
    )
    
    # User chooses input method
    print("Choose input method:")
    print("[1] Use company info string")
    print("[2] Scrape from website")
    choice = input("Enter your choice (1 or 2): ").strip()

    # Loop to allow regeneration or acceptance of the message
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
            # Scrape website content
            response = tavily_client.extract(website_link,include_images=False,include_favicon=False,extract_depth='advanced',format='Text')
            full_website_content = " ".join(r["raw_content"] for r in response["results"])
            website_content = " ".join(full_website_content.split()[:300])

            # Step 1: generate the first message immediately
            output = generate_personalised_with_website(company, website_content, club_info)
            print("\nGenerated message:")
            print(output)

            # Step 2: ask if the user wants to regenerate
            wants_to_regenerate = input("\nDo you want to regenerate? (y/n): ").strip().lower()
            if wants_to_regenerate != "y":
                print("\nMessage accepted.")
                break

            # Step 3: show scraped content and ask if it looks good
            print("\n--- Scraped Website Content Preview (First ~300 words) ---")
            print(response["results"][0]["raw_content"][:5000])  # Show first ~300 words
            print("-----------------------------------------------------------\n")
            satisfied = input("Are you happy with the scraped content? (y/n): ").strip().lower()

            if satisfied == "y":
                while True:
                    output = generate_personalised_with_website(company, website_content, club_info)
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

# Example usage
if __name__ == "__main__":
    # Example usage
    company_name = "Ed STEM"
    website_link = "https://edstem.org/about"
    company_info_string = (
        "We recently collaborated with In-Logic, a leading provider of IT solutions and services. We would love to explore potential sponsorship opportunities with them."
    )

    run_personalised_message(company_name, website_link, company_info_string)