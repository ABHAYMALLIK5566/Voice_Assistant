from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")

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
            output.innerHTML = ""
        }
    </script>
</body>

</html>'''

HtmlCode = str(HtmlCode).replace("recognition.lang = '';",f"recognition.lang = '{InputLanguage}';")

with open(r"Data\Voice.html","w") as f:
      f.write(HtmlCode)

current_dir = os.getcwd()
Link = f"{current_dir}\Data\Voice.html"
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
service = Service(ChromeDriverManager().install())
driver = None

def initialize_driver():
    """Initialize or reinitialize the Chrome driver"""
    global driver
    try:
        if driver:
            try:
                driver.quit()
            except:
                pass
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("[SpeechToText] Chrome driver initialized successfully")
        return True
    except Exception as e:
        print(f"[SpeechToText] Error initializing Chrome driver: {e}")
        return False

# Initialize driver on module load
initialize_driver()

TempDirPath = rf"{current_dir}\Frontend\Files"

def SetAssistantStatus(Status):
      
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):

    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom","can you","what's","where's","how's", "can you"]

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
    return english_translation.capitalize()

def SpeechRecognition():
    global driver
    
    # Check if driver is still valid, if not reinitialize
    try:
        driver.current_url
    except:
        print("[SpeechToText] Chrome driver disconnected, reinitializing...")
        if not initialize_driver():
            return None
    
    try:
        driver.get("file:///" + Link)
        driver.find_element(by=By.ID,value="start").click()
    except Exception as e:
        if "disconnected" in str(e) or "chrome not reachable" in str(e):
            print("[SpeechToText] Chrome disconnected during setup, reinitializing...")
            if not initialize_driver():
                return None
            try:
                driver.get("file:///" + Link)
                driver.find_element(by=By.ID,value="start").click()
            except Exception as e2:
                print(f"[SpeechToText] Failed to reinitialize: {e2}")
                return None
        else:
            print(f"[SpeechToText] Error setting up speech recognition: {e}")
            return None

    while True:
        try:
            Text = driver.find_element(by=By.ID,value="output").text

            if Text:
                driver.find_element(by=By.ID,value="end").click()
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))

        except Exception as e:
            if "disconnected: not connected to DevTools" in str(e) or "chrome not reachable" in str(e) or "disconnected: unable to send message to renderer" in str(e):
                print("[SpeechToText] Chrome disconnected, reinitializing driver...")
                if initialize_driver():
                    # Restart the speech recognition process
                    try:
                        driver.get("file:///" + Link)
                        driver.find_element(by=By.ID,value="start").click()
                        continue  # Continue the loop with the new driver
                    except Exception as e2:
                        print(f"[SpeechToText] Failed to restart after reinitialization: {e2}")
                        return None
                else:
                    print("[SpeechToText] Failed to reinitialize Chrome driver")
                    return None
            # For other errors, just continue trying
            pass

if __name__ == "__main__":
      
    while True:
        
        Text = SpeechRecognition()
        print(Text)

