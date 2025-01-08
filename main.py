import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
from webdriver_manager.chrome import ChromeDriverManager
import pytesseract
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set your bot token
TOKEN = "6775360865:AAHx6kPD3hV2OeryxDXN_dbWhgHZI5D49BU"

# Set the login URL
login_url = 'https://vadana48.ec.iau.ir/login/index.php'  # Replace with the actual login submission URL

# Set your login credentials
username = ''
password = ''

# Set the target URL
target_url = 'https://vadana48.ec.iau.ir/course/view.php?id=12363'  # Replace with your actual target URL

# Set the interval for checking for updates in seconds
check_interval = 300  # 5 minutes, adjust as needed

# Set up CSV file
csv_file = 'quiz_data.csv'

# Initialize Chrome WebDriver
driver = driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Function to start the scraping process
def stop_scraping(context: CallbackContext):
    global driver
    if driver:
        driver.quit()
        driver = None
        print("Scraping process stopped.")

# Create the Updater and pass it the bot's token
updater = Updater(TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# Start the scraping process
try:
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Open the login page
    driver.get(login_url)

    # Wait for the login form to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))

    # Find and fill in the username field
    username_field = driver.find_element(By.NAME, 'username')
    username_field.send_keys(username)

    # Find and fill in the password field
    password_field = driver.find_element(By.NAME, 'password')
    password_field.send_keys(password)

    # Find the captcha image element
    captcha_img_element = driver.find_element(By.XPATH, '//div[@id="captcha-row"]//img')

    # Get the captcha image source URL
    captcha_img_url = captcha_img_element.get_attribute('src')

    # Download the captcha image using Selenium
    captcha_img_data = captcha_img_element.screenshot_as_png
    captcha_img = Image.open(BytesIO(captcha_img_data))

    # Use Tesseract to extract text from the captcha image
    captcha_text = pytesseract.image_to_string(captcha_img)

    # Find and fill in the captcha field
    captcha_field = driver.find_element(By.NAME, 'captcha')
    captcha_field.send_keys(captcha_text)

    # Find and submit the login button
    login_button = driver.find_element(By.ID, 'loginBtn')
    login_button.click()

    # Navigate to the target URL
    time.sleep(6)
    driver.get(target_url)

    existing_links = set()

    # After successful login and redirect to the target URL
    while True:
        # Get the page source after waiting for elements to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "mod/quiz")]')))
        page_source = driver.page_source

        # Find all links with 'mod/quiz' in the href attribute
        quiz_links = driver.find_elements(By.XPATH, '//a[contains(@href, "mod/quiz")]')

        # Write new data to the CSV file
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)

            # Variable to track if new links were found
            new_links_found = False

            # Iterate through quiz links and write title and URL to the CSV file
            for link in quiz_links:
                title = link.text.strip()
                url = link.get_attribute('href')

                # Check if the URL is not in the existing set
                if url not in existing_links:
                    # Write data to the CSV file
                    csv_writer.writerow([title, url])
                    print(f'New Quiz Found - Title: {title}, URL: {url}')
                    existing_links.add(url)
                    new_links_found = True

            # Check if no new links were found
            if not new_links_found:
                print('No new links found.')

        # Wait for the next check interval
        time.sleep(300)  # 5 minutes, adjust as needed

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Stop the scraping process
    stop_scraping(None)

# Function to start the bot
def start(update, context):
    try:
        # Read the latest link and timestamp from the CSV file
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            latest_link = None
            timestamp = None
            title = None
            for row in csv_reader:
                if len(row) > 1:
                    title = row[0]
                    latest_link = row[1]
                    timestamp = row[2] if len(row) > 2 else None

            if latest_link:
                message = f"Latest link in CSV file:\nTitle: {title}\nURL: {latest_link}\nTimestamp: {timestamp}"
            else:
                message = "CSV file is empty."

        # Send the message to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send /startscraping to start the scraping process.")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {str(e)}")
# Register command handlers
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("stopscraping", stop_scraping))

# Start the Bot
updater.start_polling()

# Run the bot until you send a signal to stop with Ctrl+C
updater.idle()
