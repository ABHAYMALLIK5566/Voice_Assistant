import pygame
import random
import asyncio
import edge_tts
import os
import threading
import time
from dotenv import dotenv_values
import uuid

# Global flag for TTS interruption
TTS_PLAYING = False
TTS_STOP_FLAG = False

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-CA-LiamNeural")

def stop_tts():
    """Stop the currently playing TTS"""
    global TTS_STOP_FLAG, TTS_PLAYING
    TTS_STOP_FLAG = True
    TTS_PLAYING = False
    print("[TTS] Stopping speech...")

def is_tts_playing():
    """Check if TTS is currently playing"""
    return TTS_PLAYING

async def _tts_async(text):
    global TTS_PLAYING, TTS_STOP_FLAG
    TTS_PLAYING = True
    TTS_STOP_FLAG = False
    unique_id = str(uuid.uuid4())
    tts_file = f"Data/speech_{unique_id}.mp3"
    try:
        print(f"[TTS] Generating speech for: {text[:50]}...")
        communicate = edge_tts.Communicate(text, AssistantVoice)
        await communicate.save(tts_file)
        if TTS_STOP_FLAG:
            print("[TTS] Speech interrupted before playing")
            return
        print("[TTS] Playing speech...")
        pygame.mixer.init()
        pygame.mixer.music.load(tts_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and not TTS_STOP_FLAG:
            time.sleep(0.1)
        if TTS_STOP_FLAG:
            pygame.mixer.music.stop()
            print("[TTS] Speech interrupted during playback")
        else:
            print("[TTS] Speech completed successfully")
    except Exception as e:
        print(f"[TTS] Error: {e}")
    finally:
        TTS_PLAYING = False
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        # Clean up the TTS file
        try:
            if os.path.exists(tts_file):
                os.remove(tts_file)
        except Exception as cleanup_err:
            print(f"[TTS] Cleanup error: {cleanup_err}")

def TextToSpeech(text):
    """Convert text to speech with interruption capability"""
    global TTS_PLAYING, TTS_STOP_FLAG
    
    # Stop any currently playing speech
    if TTS_PLAYING:
        stop_tts()
        time.sleep(0.5)  # Brief pause to ensure clean stop
    
    # Start new speech in a separate thread
    def run_tts():
        asyncio.run(_tts_async(text))
    
    tts_thread = threading.Thread(target=run_tts)
    tts_thread.daemon = True
    tts_thread.start()
    
    print(f"[TTS] Started speaking: {text[:50]}...")

def check_for_interruption(audio_text):
    """Check if the audio text contains interruption keywords"""
    # Only interrupt if it's a clear wake word or stop command
    # Don't interrupt if "jarvis" is part of a normal question
    audio_lower = audio_text.lower().strip()
    
    # Clear interruption commands
    if audio_lower in ['stop', 'halt', 'pause', 'shut up']:
        print(f"[TTS] Interruption keyword detected: {audio_lower}")
        stop_tts()
        return True
    
    # Wake word detection - only if it's a standalone "jarvis" or starts with "jarvis"
    if audio_lower == 'jarvis' or audio_lower.startswith('jarvis '):
        # Check if it's just "jarvis" or "jarvis" followed by a command
        if audio_lower == 'jarvis' or len(audio_lower.split()) <= 3:
            print(f"[TTS] Wake word detected: {audio_lower}")
            stop_tts()
            return True
    
    # Don't interrupt for normal conversation like "how are you jarvis?"
    return False

def TTS(Text, func=lambda r=None: True):
    """Legacy TTS function for compatibility"""
    TextToSpeech(Text)

if __name__ == "__main__":  
    while True:
        TextToSpeech(input("Enter the text : "))

