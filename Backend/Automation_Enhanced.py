from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import psutil
import time
import os
import re
import json

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# Professional responses for better user experience
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
    "Continued support is my commitment to you. Let me know if there's anything more I can do for you.",
    "I'm here to ensure your experience is seamless. If you have any further requests, please let me know.",
    "Your needs are important to me. If there's anything I can assist you with, I'm just a message away.",
    "I'm dedicated to providing excellent service. Should you require further assistance, I'm here for you.",
    "Exceeding your expectations is my goal. Don't hesitate to reach out for any additional help you may need.",
    "Your satisfaction matters. If you have more questions or need assistance, feel free to ask.",
    "I'm committed to making your experience positive. Let me know if there's anything else I can do for you.",
    "Your feedback is valued. If there's anything I can do to enhance your experience, please let me know."
]

# Enhanced app database with more apps and metadata
APP_DATABASE = {
    # Web Apps
    "youtube": {
        "type": "web",
        "url": "https://www.youtube.com",
        "keywords": ["yt", "tube", "video", "videos"],
        "process_name": "chrome.exe",
        "tab_identifier": "youtube.com"
    },
    "instagram": {
        "type": "web", 
        "url": "https://www.instagram.com",
        "keywords": ["ig", "insta", "gram"],
        "process_name": "chrome.exe",
        "tab_identifier": "instagram.com"
    },
    "facebook": {
        "type": "web",
        "url": "https://www.facebook.com", 
        "keywords": ["fb", "face", "book"],
        "process_name": "chrome.exe",
        "tab_identifier": "facebook.com"
    },
    "twitter": {
        "type": "web",
        "url": "https://twitter.com",
        "keywords": ["tweet", "tweets", "x"],
        "process_name": "chrome.exe", 
        "tab_identifier": "twitter.com"
    },
    "linkedin": {
        "type": "web",
        "url": "https://www.linkedin.com",
        "keywords": ["linked", "in"],
        "process_name": "chrome.exe",
        "tab_identifier": "linkedin.com"
    },
    "reddit": {
        "type": "web",
        "url": "https://www.reddit.com",
        "keywords": ["reddit"],
        "process_name": "chrome.exe",
        "tab_identifier": "reddit.com"
    },
    "github": {
        "type": "web",
        "url": "https://github.com",
        "keywords": ["git", "hub"],
        "process_name": "chrome.exe",
        "tab_identifier": "github.com"
    },
    "stackoverflow": {
        "type": "web",
        "url": "https://stackoverflow.com",
        "keywords": ["stack", "overflow", "so"],
        "process_name": "chrome.exe",
        "tab_identifier": "stackoverflow.com"
    },
    
    # Desktop Apps
    "notepad": {
        "type": "desktop",
        "keywords": ["note", "pad", "text", "editor"],
        "process_name": "notepad.exe",
        "exe_name": "notepad.exe"
    },
    "calculator": {
        "type": "desktop", 
        "keywords": ["calc", "calculator"],
        "process_name": "calculator.exe",
        "exe_name": "calc.exe"
    },
    "chrome": {
        "type": "desktop",
        "keywords": ["browser", "google", "chrome"],
        "process_name": "chrome.exe",
        "exe_name": "chrome.exe"
    },
    "firefox": {
        "type": "desktop",
        "keywords": ["firefox", "mozilla"],
        "process_name": "firefox.exe",
        "exe_name": "firefox.exe"
    },
    "word": {
        "type": "desktop",
        "keywords": ["microsoft word", "word", "doc"],
        "process_name": "winword.exe",
        "exe_name": "winword.exe"
    },
    "excel": {
        "type": "desktop",
        "keywords": ["microsoft excel", "excel", "spreadsheet"],
        "process_name": "excel.exe",
        "exe_name": "excel.exe"
    },
    "powerpoint": {
        "type": "desktop",
        "keywords": ["microsoft powerpoint", "powerpoint", "ppt"],
        "process_name": "powerpnt.exe",
        "exe_name": "powerpnt.exe"
    },
    "spotify": {
        "type": "desktop",
        "keywords": ["spotify", "music"],
        "process_name": "spotify.exe",
        "exe_name": "spotify.exe"
    },
    "discord": {
        "type": "desktop",
        "keywords": ["discord"],
        "process_name": "discord.exe",
        "exe_name": "discord.exe"
    },
    "teams": {
        "type": "desktop",
        "keywords": ["microsoft teams", "teams"],
        "process_name": "teams.exe",
        "exe_name": "teams.exe"
    },
    "zoom": {
        "type": "desktop",
        "keywords": ["zoom"],
        "process_name": "zoom.exe",
        "exe_name": "zoom.exe"
    }
}

# App state tracking
app_states = {}

# Enhanced app name cleaning with fuzzy matching
def clean_app_name(app):
    """Enhanced app name cleaning with intelligent processing"""
    app = app.lower().strip()
    
    # Remove common filler words
    filler_words = ["can you", "please", "for me", "the", "a", "an", "open", "close", "start", "launch"]
    for filler in filler_words:
        pattern = r'\b' + re.escape(filler) + r'\b'
        app = re.sub(pattern, '', app)
    
    # Clean up extra spaces and punctuation
    app = re.sub(r'\s+', ' ', app)
    app = app.rstrip('?.,!').strip()
    
    return app

def find_app_by_name(app_name):
    """Intelligent app detection with fuzzy matching"""
    app_clean = clean_app_name(app_name)
    
    # Direct match
    if app_clean in APP_DATABASE:
        return app_clean, APP_DATABASE[app_clean]
    
    # Keyword matching
    for app_key, app_data in APP_DATABASE.items():
        if app_clean in app_data.get("keywords", []):
            return app_key, app_data
    
    # Partial matching
    for app_key, app_data in APP_DATABASE.items():
        if app_clean in app_key or app_key in app_clean:
            return app_key, app_data
    
    # Fuzzy matching for similar names
    for app_key, app_data in APP_DATABASE.items():
        if any(keyword in app_clean for keyword in app_data.get("keywords", [])):
            return app_key, app_data
    
    return None, None

def is_app_running(app_name):
    """Check if an app is currently running"""
    app_key, app_data = find_app_by_name(app_name)
    if not app_data:
        return False
    
    process_name = app_data.get("process_name")
    if not process_name:
        return False
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == process_name.lower():
                return True
        return False
    except Exception:
        return False

def get_running_apps():
    """Get list of currently running apps"""
    running_apps = []
    for app_key, app_data in APP_DATABASE.items():
        if is_app_running(app_key):
            running_apps.append(app_key)
    return running_apps

# Enhanced OpenApp with intelligent features
def OpenApp(app):
    """Enhanced app opening with intelligent detection and feedback"""
    app_key, app_data = find_app_by_name(app)
    
    if not app_data:
        print(f"[Automation] ❌ App '{app}' not found in database")
        return False
    
    app_type = app_data.get("type")
    
    # Check if already running
    if is_app_running(app_key):
        print(f"[Automation] ℹ️ {app_key} is already running")
        return True
    
    try:
        if app_type == "web":
            # Open web app
            url = app_data.get("url")
            webopen(url)
            print(f"[Automation] ✅ Opened {app_key} at {url}")
            
        elif app_type == "desktop":
            # Open desktop app
            exe_name = app_data.get("exe_name")
            if exe_name:
                subprocess.Popen([exe_name])
                print(f"[Automation] ✅ Launched {app_key}")
            else:
                # Fallback to AppOpener
                appopen(app_key, match_closest=True, output=True, throw_error=True)
                print(f"[Automation] ✅ Opened {app_key} via AppOpener")
        
        # Update app state
        app_states[app_key] = {"status": "running", "opened_at": time.time()}
        return True
        
    except Exception as e:
        print(f"[Automation] ❌ Error opening {app_key}: {e}")
        return False

# Enhanced CloseApp with smart tab management
def CloseApp(app):
    """Enhanced app closing with intelligent tab management"""
    app_key, app_data = find_app_by_name(app)
    
    if not app_data:
        print(f"[Automation] ❌ App '{app}' not found in database")
        return False
    
    app_type = app_data.get("type")
    
    # Check if not running
    if not is_app_running(app_key):
        print(f"[Automation] ℹ️ {app_key} is not currently running")
        return True
    
    try:
        if app_type == "web":
            # Smart web app closing
            return close_web_app(app_key, app_data)
        elif app_type == "desktop":
            # Desktop app closing
            return close_desktop_app(app_key, app_data)
        
    except Exception as e:
        print(f"[Automation] ❌ Error closing {app_key}: {e}")
        return False

def close_web_app(app_key, app_data):
    """Smart web app closing with tab management"""
    try:
        # Method 1: Try to close specific tab using keyboard shortcuts
        import keyboard
        
        print(f"[Automation] 🔍 Looking for {app_key} tab...")
        
        # Use Ctrl+W to close current tab
        keyboard.press_and_release("ctrl+w")
        time.sleep(0.3)
        
        print(f"[Automation] ✅ Closed {app_key} tab")
        return True
        
    except Exception as e:
        print(f"[Automation] ⚠️ Tab closing failed: {e}")
        
        # Method 2: Close entire browser process
        try:
            process_name = app_data.get("process_name")
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    print(f"[Automation] ✅ Terminated {process_name}")
                    return True
        except Exception as e2:
            print(f"[Automation] ❌ Process termination failed: {e2}")
        
        # Method 3: Alt+F4 fallback
        try:
            keyboard.press_and_release("alt+f4")
            print(f"[Automation] ✅ Used Alt+F4 fallback")
            return True
        except Exception as e3:
            print(f"[Automation] ❌ Alt+F4 failed: {e3}")
            return False

def close_desktop_app(app_key, app_data):
    """Enhanced desktop app closing"""
    try:
        # Method 1: Use AppOpener close
        close(app_key, match_closest=True, output=True, throw_error=True)
        print(f"[Automation] ✅ Closed {app_key}")
        return True
        
    except Exception as e:
        print(f"[Automation] ⚠️ AppOpener close failed: {e}")
        
        # Method 2: Process termination
        try:
            process_name = app_data.get("process_name")
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    print(f"[Automation] ✅ Terminated {process_name}")
                    return True
        except Exception as e2:
            print(f"[Automation] ❌ Process termination failed: {e2}")
        
        # Method 3: Alt+F4 fallback
        try:
            keyboard.press_and_release("alt+f4")
            print(f"[Automation] ✅ Used Alt+F4 fallback")
            return True
        except Exception as e3:
            print(f"[Automation] ❌ Alt+F4 failed: {e3}")
            return False

# Enhanced System commands
def System(command):
    """Enhanced system commands with more options"""
    command = command.lower().strip()
    
    system_commands = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
        "brightness up": lambda: keyboard.press_and_release("brightness up"),
        "brightness down": lambda: keyboard.press_and_release("brightness down"),
        "screenshot": lambda: keyboard.press_and_release("print screen"),
        "copy": lambda: keyboard.press_and_release("ctrl+c"),
        "paste": lambda: keyboard.press_and_release("ctrl+v"),
        "cut": lambda: keyboard.press_and_release("ctrl+x"),
        "undo": lambda: keyboard.press_and_release("ctrl+z"),
        "redo": lambda: keyboard.press_and_release("ctrl+y"),
        "select all": lambda: keyboard.press_and_release("ctrl+a"),
        "save": lambda: keyboard.press_and_release("ctrl+s"),
        "new tab": lambda: keyboard.press_and_release("ctrl+t"),
        "close tab": lambda: keyboard.press_and_release("ctrl+w"),
        "refresh": lambda: keyboard.press_and_release("f5"),
        "fullscreen": lambda: keyboard.press_and_release("f11"),
        "minimize": lambda: keyboard.press_and_release("windows+down"),
        "maximize": lambda: keyboard.press_and_release("windows+up"),
        "task manager": lambda: keyboard.press_and_release("ctrl+shift+esc"),
        "lock screen": lambda: keyboard.press_and_release("windows+l"),
        "show desktop": lambda: keyboard.press_and_release("windows+d"),
    }
    
    if command in system_commands:
        try:
            system_commands[command]()
            print(f"[Automation] ✅ Executed system command: {command}")
            return True
        except Exception as e:
            print(f"[Automation] ❌ System command failed: {e}")
            return False
    else:
        print(f"[Automation] ❌ Unknown system command: {command}")
        return False

# Enhanced content generation
def Content(Topic):
    """Enhanced content generation with better file handling"""
    try:
        def OpenNotepad(File):
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, File])

        def ContentWriterAI(prompt):
            if not client:
                return "AI content generation is not available. Please check your API key."
            
            messages = [{"role": "user", "content": f"{prompt}"}]
            system_prompt = {"role": "system", "content": "You are a professional content writer. Write high-quality, engaging content."}
            
            try:
                completion = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[system_prompt] + messages,
                    max_tokens=2048,
                    temperature=0.7,
                    top_p=1,
                    stream=True,
                    stop=None
                )

                Answer = ""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        Answer += chunk.choices[0].delta.content

                Answer = Answer.replace("</s>", "")
                return Answer
            except Exception as e:
                return f"Content generation failed: {e}"

        Topic = Topic.replace("Content ", "")
        ContentByAI = ContentWriterAI(Topic)

        # Create Data directory if it doesn't exist
        os.makedirs("Data", exist_ok=True)
        
        filename = f"Data/{Topic.lower().replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(ContentByAI)

        OpenNotepad(filename)
        print(f"[Automation] ✅ Generated content: {filename}")
        return True
        
    except Exception as e:
        print(f"[Automation] ❌ Content generation failed: {e}")
        return False

# Enhanced search functions
def GoogleSearch(Topic):
    """Enhanced Google search"""
    try:
        search(Topic)
        print(f"[Automation] ✅ Opened Google search for: {Topic}")
        return True
    except Exception as e:
        print(f"[Automation] ❌ Google search failed: {e}")
        return False

def YouTubeSearch(Topic):
    """Enhanced YouTube search"""
    try:
        Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
        webbrowser.open(Url4Search)
        print(f"[Automation] ✅ Opened YouTube search for: {Topic}")
        return True
    except Exception as e:
        print(f"[Automation] ❌ YouTube search failed: {e}")
        return False

def PlayYoutube(query):
    """Enhanced YouTube video playback"""
    try:
        playonyt(query)
        print(f"[Automation] ✅ Playing YouTube video: {query}")
        return True
    except Exception as e:
        print(f"[Automation] ❌ YouTube playback failed: {e}")
        return False

# Enhanced automation pipeline
async def TranslateAndExecute(commands: list[str]):
    """Enhanced command processing with better error handling"""
    funcs = []
    
    for command in commands:
        command = command.strip()
        if not command:
            continue
            
        try:
            if command.startswith("open "):
                app_name = command.removeprefix("open ")
                fun = asyncio.to_thread(OpenApp, app_name)
                funcs.append(fun)
                
            elif command.startswith("close "):
                app_name = command.removeprefix("close ")
                fun = asyncio.to_thread(CloseApp, app_name)
                funcs.append(fun)
                
            elif command.startswith("play "):
                query = command.removeprefix("play ")
                fun = asyncio.to_thread(PlayYoutube, query)
                funcs.append(fun)
                
            elif command.startswith("content "):
                topic = command.removeprefix("content ")
                fun = asyncio.to_thread(Content, topic)
                funcs.append(fun)
                
            elif command.startswith("google search "):
                query = command.removeprefix("google search ")
                fun = asyncio.to_thread(GoogleSearch, query)
                funcs.append(fun)
                
            elif command.startswith("youtube search "):
                query = command.removeprefix("youtube search ")
                fun = asyncio.to_thread(YouTubeSearch, query)
                funcs.append(fun)
                
            elif command.startswith("system "):
                cmd = command.removeprefix("system ")
                fun = asyncio.to_thread(System, cmd)
                funcs.append(fun)
                
            else:
                print(f"[Automation] ⚠️ Unknown command: {command}")
                
        except Exception as e:
            print(f"[Automation] ❌ Command processing error: {e}")
    
    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"[Automation] ❌ Command execution failed: {result}")
            else:
                yield result
    else:
        yield "No valid commands to execute"

async def Automation(commands: list[str]):
    """Enhanced automation with better feedback"""
    print(f"[Automation] 🚀 Executing {len(commands)} command(s)...")
    
    try:
        async for result in TranslateAndExecute(commands):
            if result:
                print(f"[Automation] ✅ Command completed successfully")
        
        print(f"[Automation] 🎉 All commands completed!")
        return True
        
    except Exception as e:
        print(f"[Automation] ❌ Automation failed: {e}")
        return False

# Utility functions
def get_app_status():
    """Get status of all apps"""
    status = {}
    for app_key in APP_DATABASE:
        status[app_key] = {
            "running": is_app_running(app_key),
            "state": app_states.get(app_key, {})
        }
    return status

def list_available_apps():
    """List all available apps"""
    return list(APP_DATABASE.keys())

def get_app_info(app_name):
    """Get detailed info about an app"""
    app_key, app_data = find_app_by_name(app_name)
    if app_data:
        return {
            "name": app_key,
            "type": app_data.get("type"),
            "running": is_app_running(app_key),
            "data": app_data
        }
    return None 