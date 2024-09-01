import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define the URLs
login_url = "http://results.veltech.edu.in/Stulogin/index.aspx"
results_url = "http://results.veltech.edu.in/Stulogin/UserPages/StudentUniversityResultsBySem.aspx"

# Define the headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Pragma": "no-cache",
    "Accept": "*/*"
}

# Function to log in and fetch results
def fetch_results(username: str, password: str, semester: str) -> str:
    session = requests.Session()

    try:
        # Get the login page to retrieve VIEWSTATE and EVENTVALIDATION
        response = session.get(login_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract VIEWSTATE and EVENTVALIDATION
        viewstate = soup.find(id="__VIEWSTATE")['value']
        eventvalidation = soup.find(id="__EVENTVALIDATION")['value']

        # Define the login payload
        login_payload = {
            "__LASTFOCUS": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": "59D1681B",
            "__EVENTVALIDATION": eventvalidation,
            "txtUserName": username,
            "txtPassword": password,
            "LoginButton.x": "29",
            "LoginButton.y": "8"
        }

        # Perform the login
        login_response = session.post(login_url, data=login_payload, headers=headers)

        # Check if login was successful
        if "Logout" in login_response.text:
            # Get the results page
            results_response = session.get(results_url, headers=headers)
            results_soup = BeautifulSoup(results_response.text, 'html.parser')

            # Extract VIEWSTATE and EVENTVALIDATION for results page
            viewstate_results = results_soup.find(id="__VIEWSTATE")['value']
            eventvalidation_results = results_soup.find(id="__EVENTVALIDATION")['value']

            # Define the results payload
            results_payload = {
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ddlSemester",
                "__EVENTARGUMENT": "",
                "__LASTFOCUS": "",
                "__VIEWSTATE": viewstate_results,
                "__VIEWSTATEGENERATOR": "F6423605",
                "__EVENTVALIDATION": eventvalidation_results,
                "ctl00$ContentPlaceHolder1$ddlSemester": semester
            }

            # Request the results
            results_post_response = session.post(results_url, data=results_payload, headers=headers)

            # Parse and extract the results
            results_soup = BeautifulSoup(results_post_response.text, 'html.parser')
            subjects = results_soup.find_all('td', style="width:350px;")
            grades = results_soup.find_all('td', style="width:60px;")
            grades=grades[2::4]
            results = []
            for subject, grade in zip(subjects, grades):
                results.append(f"Subject: {subject.text.strip()}, Grade: {grade.text.strip()}")
            return "\n".join(results)
        else:
            return "Login failed. Please check your credentials."
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "An error occurred while fetching results."

# Command handler for the /results command
def results_command(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 3:
        update.message.reply_text("Usage: /results <username> <password> <semester>")
        return

    username, password, semester = context.args
    results = fetch_results(username, password, semester)
    update.message.reply_text(results)

def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token ='7539040621:AAHWWpdq02zuTp66nGDHy7_orGRNC6M20Ks'

    # Create the Updater and pass it your bot's token
    updater = Updater(token=bot_token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("results", results_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()
