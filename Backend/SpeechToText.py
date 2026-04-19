from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import mtranslate as mt

# Load environment variables
load_dotenv()
InputLanguage = os.getenv("InputLanguage", "en")

# HTML content with speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Inject Input Language
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save HTML to file
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Construct local file URL
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

# Set Chrome options - Using regular Chrome instead of Beta
chrome_options = Options()

# Try Chrome Beta first, fallback to regular Chrome
chrome_beta_path = r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
chrome_regular_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

if os.path.exists(chrome_beta_path):
    chrome_options.binary_location = chrome_beta_path
    print("Using Chrome Beta")
elif os.path.exists(chrome_regular_path):
    chrome_options.binary_location = chrome_regular_path
    print("Using regular Chrome")
else:
    print("Chrome not found at standard locations. Using system default.")

chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # Modern headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Try to use the ChromeDriver, or let Selenium manage it automatically
chrome_driver_path = r"D:\VARSI\chromedriver-win64 (2)\chromedriver-win64\chromedriver.exe"

try:
    if os.path.exists(chrome_driver_path):
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"Using ChromeDriver from: {chrome_driver_path}")
    else:
        # Let Selenium automatically manage ChromeDriver
        driver = webdriver.Chrome(options=chrome_options)
        print("Using automatically managed ChromeDriver")
except Exception as e:
    print(f"Error initializing Chrome: {e}")
    print("\nTrying with Selenium's automatic driver management...")
    driver = webdriver.Chrome(options=chrome_options)

# Setup temp status path
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation

def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text:
                driver.find_element(By.ID, "end").click()
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass

# Run the assistant
if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            print(Text)
    except KeyboardInterrupt:
        print("\nStopping speech recognition...")
        driver.quit()
    except Exception as e:
        print(f"Error: {e}")
        driver.quit()