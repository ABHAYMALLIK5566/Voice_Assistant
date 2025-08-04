from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit.misc import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import json
import websockets
from chrome_tab_closer import tab_closer_server

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
classes = ["zCubwf","hgKElc","LTKOO sY7ric","Z0LcW","gsrt vk_bk FzvWSb YwPhnf","pclqee","tw-Data-text tw-text-small tw-ta","IZ6rdc","O5uR6d LTKOO","vlzY6d","webanswers-webanswers_table__webanswers-table","dDoNo ikb4Bb gsrt","sXLaOe","LWkfKe","VQF4g","qv3Wpe","kno-rdesc","SPZz6b"]
useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
client = Groq(api_key=GroqAPIKey)
professional_responses = ["Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.","I'm at your service for any additional questions or support you may need—don't hesitate to ask.","Continued support is my commitment to you. Let me know if there's anything more I can do for you.","I'm here to ensure your experience is seamless. If you have any further requests, please let me know.","Your needs are important to me. If there's anything I can assist you with, I'm just a message away.","I'm dedicated to providing excellent service. Should you require further assistance, I'm here for you.","Exceeding your expectations is my goal. Don't hesitate to reach out for any additional help you may need.","Your satisfaction matters. If you have more questions or need assistance, feel free to ask.","I'm committed to making your experience positive. Let me know if there's anything else I can do for you.","Your feedback is valued. If there's anything I can do to enhance your experience, please let me know.","If there's anything specific you'd like assistance with, please share, and I'll be happy to help.","Your concerns are important to me. Feel free to ask for further guidance or information.","I'm here to address any additional queries or provide clarification as needed.","For a seamless experience, let me know if there's anything else you require assistance with.","Your satisfaction is key; if there's a specific area you'd like more support in, I'm here for you.","Don't hesitate to let me know if there's a particular aspect you'd like further clarification on.","I aim to make your interaction effortless. If there's more you need, feel free to inform me.","Your input is valuable. Please share any additional requirements, and I'll respond promptly.","Should you require more details or have additional questions, I'm ready to provide assistance.","Your success is important to me. If there's anything else you need support with, feel free to ask."]
messages = []
SystemChatBot = [{"role": "system","content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

def GoogleSearch(Topic):
      search(Topic)
      return True

def Content(Topic):

      def OpenNotepad(File):
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, File])

      def ContentWriterAI(prompt):
      
            messages.append({"role": "user", "content": f"{prompt}"})
            completion = client.chat.completions.create(
            model = "mixtral-8x7b-32768",
            messages = SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None)

            Answer =""
            for chunk in completion:
                  if chunk.choices[0].delta.content:
                        Answer += chunk.choices[0].delta.content

            Answer = Answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": Answer})
            return Answer

      topic_str: str = Topic.replace("Content ", "")
      ContentByAI = ContentWriterAI(topic_str)

      with open(rf"Data\{topic_str.lower().replace(' ','')}.txt","w",encoding="utf-8") as file:
            file.write(ContentByAI)
            file.close()

      OpenNotepad(rf"Data\{topic_str.lower().replace(' ','')}.txt")
      return True

def YouTubeSearch(Topic):
      Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
      webbrowser.open(Url4Search)
      return True

def PlayYoutube(query):
      playonyt(query)
      return True

def OpenApp(app, sess=requests.session()):
    
      try:
            appopen(app,match_closest=True, output=True, throw_error=True)
            return True
    
      except:
        
            def extract_links(html):
                  if html is None:
                        return []
                  soup = BeautifulSoup(html, 'html.parser')
                  links = soup.find_all('a', {'jsname': 'UWckNb'})
                  return [link.get('href') for link in links]
            
            def search_google(query):
                  url = f"https://www.google.com/search?q={query}"
                  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
                  response = sess.get(url, headers=headers)

                  if response.status_code == 200:
                        return response.text
                  
                  else:
                        print("Failed to retrieve search results.")
                  return None
            
            html = search_google(app)

            if html:
                  link = extract_links(html)[0]
                  webopen(link)

            return True

def close_chrome_tab_by_url(url_fragment):
    """Send a WebSocket command to the Chrome extension to close a tab by URL fragment."""
    async def send_command():
        try:
            async with websockets.connect("ws://localhost:8765") as websocket:
                command = {"action": "close_tab", "url": url_fragment}
                await websocket.send(json.dumps(command))
        except Exception as e:
            print(f"[Automation] ❌ Could not send close tab command: {e}")
    # Run the async function in the event loop
    try:
        asyncio.get_event_loop().run_until_complete(send_command())
    except RuntimeError:
        # If already in an event loop (e.g., in Jupyter), use create_task
        asyncio.create_task(send_command())

def CloseApp(app):
    app = app.strip().lower()
    # If it's a URL or web app, use the Chrome extension
    if "." in app or "http" in app:
        print(f"[Automation] 🔗 Attempting to close Chrome tab with: {app}")
        close_chrome_tab_by_url(app)
        return True
    # Otherwise, fallback to AppOpener for desktop apps
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        return False

def System(command):
    
      def mute():
            keyboard.press_and_release("volume mute")

      def unmute():
            keyboard.press_and_release("volume mute")

      def volume_up():
            keyboard.press_and_release("volume up")

      def volume_down():
            keyboard.press_and_release("volume down")

      if command == "mute":
            mute()

      elif command == "unmute":
            unmute()

      elif command == "volume up":
            volume_up()

      elif command == "volume down":
            volume_down()

      return True

async def TranslateAndExecute(commands: list[str]):
    
      funcs = []

      for command in commands:
        
            if command.startswith("open "):

                  if "open it" in command:
                        pass

                  if "open file" == command:
                        pass
                  
                  else:
                        fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                        funcs.append(fun)

            elif command.startswith("general "):
                  pass

            elif command.startswith("realtime "):
                  pass

            elif command.startswith("close "):
                  fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
                  funcs.append(fun)
            
            elif command.startswith("play "):
                  fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
                  funcs.append(fun)

            elif command.startswith("content "):
                  fun = asyncio.to_thread(Content, command.removeprefix("content "))
                  funcs.append(fun)

            elif command.startswith("google search "):
                  fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
                  funcs.append(fun)

            elif command.startswith("youtube search "):
                  fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
                  funcs.append(fun)

            elif command.startswith("system "):
                  fun = asyncio.to_thread(System, command.removeprefix("system "))
                  funcs.append(fun)
            
            else:
                  print(f"No Function Found. For {command}")

      results = await asyncio.gather(*funcs)

      for result in results:

            if isinstance(result, str):
                  yield result

            else:
                  yield result

async def Automation(commands: list[str]):

      async for result in TranslateAndExecute(commands):
            pass

      return True


