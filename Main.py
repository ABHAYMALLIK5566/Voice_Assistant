#!/usr/bin/env python3
"""
JARVIS - AI Assistant
Main entry point with proper backend integration and parallelism
"""

import sys
import os
import threading
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
from Frontend.GUI import AdvancedMainWindow, BlobHomeWindow, ChatWindow

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class BackendManager(QObject):
    """Centralized backend manager for coordinating all operations"""
    
    # Signals for GUI communication
    chat_response = pyqtSignal(str)  # Assistant response
    status_update = pyqtSignal(str)  # Status updates
    voice_input = pyqtSignal(str)    # Voice input received
    error_occurred = pyqtSignal(str) # Error messages
    exitRequested = pyqtSignal()     # Exit signal
    go_home_requested = pyqtSignal()
    volume_update = pyqtSignal(float)  # Volume level updates
    
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.is_sleeping = False  # New: Track sleep state
        self.current_tts_thread = None
        self.stt_thread = None
        self.processing_lock = threading.Lock()
        self.last_voice_input = None
        self.last_voice_time = 0
        self.volume_timer = QTimer()
        self.volume_timer.timeout.connect(self._update_volume)
        
        # Initialize backend modules
        self._init_backend_modules()
        self._init_volume_detection()
    
    def _init_backend_modules(self):
        """Initialize all backend modules"""
        try:
            # Import all backend modules
            from Backend.Model import FirstLayerDMM
            from Backend.Chatbot import ChatBot
            from Backend.RealtimeSearchEngine import RealtimeSearchEngine
            from Backend.Automation import Automation
            from Backend.ImageGeneration import GenerateImages
            from Backend.TextToSpeech import TextToSpeech, stop_tts, check_for_interruption
            from Backend.SpeechToText import SpeechRecognition
            
            # Store module references
            self.FirstLayerDMM = FirstLayerDMM
            self.ChatBot = ChatBot
            self.RealtimeSearchEngine = RealtimeSearchEngine
            self.Automation = Automation
            self.GenerateImages = GenerateImages
            self.TextToSpeech = TextToSpeech
            self.stop_tts = stop_tts
            self.check_for_interruption = check_for_interruption
            self.SpeechRecognition = SpeechRecognition
            
            # Override stop_tts to also reset state
            original_stop_tts = self.stop_tts
            def enhanced_stop_tts():
                original_stop_tts()
                if hasattr(self, 'current_state'):
                    self.current_state = 'idle'
            self.stop_tts = enhanced_stop_tts
            
            print("[BackendManager] All modules initialized successfully")
            
        except Exception as e:
            print(f"[BackendManager] Error initializing modules: {e}")
            self.error_occurred.emit(f"Backend initialization failed: {e}")
    
    def _init_volume_detection(self):
        """Initialize volume detection"""
        try:
            from Backend.VolumeDetector import start_volume_detection, get_volume_level
            self.start_volume_detection = start_volume_detection
            self.get_volume_level = get_volume_level
            # Start volume detection
            self.start_volume_detection()
            # Start timer to send volume updates to GUI
            self.volume_timer.start(50)  # Update every 50ms (20 FPS)
            print("[BackendManager] Volume detection initialized")
            self.volume_detection_available = True
        except Exception as e:
            print(f"[BackendManager] Error initializing volume detection: {e}")
            # Fallback: simulate volume based on state
            self.volume_detection_available = False
            self.simulated_volume = 0.0
            self.current_state = 'idle'
            # Start timer to send simulated volume updates to GUI
            self.volume_timer.start(50)  # Update every 50ms (20 FPS)
            print("[BackendManager] Using simulated volume detection")
    
    def _update_volume(self):
        """Update volume level and send to GUI"""
        if hasattr(self, 'volume_detection_available') and self.volume_detection_available:
            try:
                volume = self.get_volume_level()
                self.volume_update.emit(volume)
            except Exception as e:
                print(f"[BackendManager] Error updating volume: {e}")
        else:
            # Simulate volume based on current state
            import random
            if self.is_sleeping:
                # Sleeping state - very low volume
                self.simulated_volume = 0.02 + 0.05 * random.random()
            elif self.current_state == 'listening':
                # Simulate listening volume with some variation
                self.simulated_volume = 0.3 + 0.4 * random.random()
            elif self.current_state == 'speaking':
                # Simulate speaking volume with more variation
                self.simulated_volume = 0.5 + 0.4 * random.random()
            else:
                # Idle state - very low volume
                self.simulated_volume = 0.05 + 0.1 * random.random()
            
            self.volume_update.emit(self.simulated_volume)
    
    def process_input(self, user_input, input_type="text"):
        """Process user input (text or voice) with proper coordination"""
        if not self.is_running:
            return
        # Prevent duplicate voice input within 2 seconds
        if input_type == "voice":
            now = time.time()
            if user_input == self.last_voice_input and (now - self.last_voice_time) < 2:
                print(f"[BackendManager] Ignoring duplicate voice input: {user_input}")
                return
            self.last_voice_input = user_input
            self.last_voice_time = now
        with self.processing_lock:
            try:
                print(f"[BackendManager] Processing {input_type} input: {user_input}")
                self.status_update.emit("Processing...")
                
                # Update current state for volume simulation
                if hasattr(self, 'current_state'):
                    self.current_state = 'processing'
                
                # Home command
                if user_input.lower().strip() in ["go home", "home"]:
                    print("[BackendManager] Home command detected")
                    self.go_home_requested.emit()
                    return
                
                # Check for exit commands FIRST (before anything else)
                if user_input.lower().strip() in ['bye', 'goodbye', 'exit', 'quit', 'close']:
                    print("[BackendManager] Exit command detected")
                    self.chat_response.emit("Goodbye! Closing the application...")
                    self.status_update.emit("Closing...")
                    # Stop all operations
                    self.is_running = False
                    self.stop_tts()
                    # Emit exit signal to close application
                    self.exitRequested.emit()
                    return
                
                # Check for sleep/wake commands
                command = user_input.lower().strip()
                # Remove punctuation and common words for more flexible matching
                clean_command = command.rstrip('.,!?').strip()
                
                # Check if the command contains sleep keywords (including common misheard variations)
                sleep_keywords = [
                    'sleep jarvis', 'jarvis sleep', 'go to sleep', 'sleep',
                    'slip jarvis', 'jarvis slip', 'slip',  # Common misheard as "slip"
                    'flip jarvis', 'jarvis flip', 'flip',  # Common misheard as "flip"
                    'slip jarvis', 'jarvis slip',          # Another variation
                    'sleep please', 'slip please', 'flip please'
                ]
                is_sleep_command = any(keyword in clean_command for keyword in sleep_keywords)
                
                if is_sleep_command:
                    if not self.is_sleeping:
                        print("[BackendManager] Sleep command detected")
                        self.is_sleeping = True
                        self.chat_response.emit("Going to sleep. Say 'wake up jarvis' to wake me up.")
                        self.status_update.emit("Sleeping...")
                        self._speak_response("Going to sleep. Say 'wake up jarvis' to wake me up.")
                        if hasattr(self, 'current_state'):
                            self.current_state = 'sleeping'
                        return
                    else:
                        print("[BackendManager] Already sleeping")
                        return
                
                # Check if the command contains wake keywords (including common misheard variations)
                wake_keywords = [
                    'wake up jarvis', 'jarvis wake up', 'wake up', 'wake',
                    'wake jarvis', 'jarvis wake',           # Shorter version
                    'wake up please', 'wake please',        # With please
                    'get up jarvis', 'jarvis get up', 'get up',  # Alternative wake commands
                    'rise jarvis', 'jarvis rise', 'rise'    # Another alternative
                ]
                is_wake_command = any(keyword in clean_command for keyword in wake_keywords)
                
                if is_wake_command:
                    if self.is_sleeping:
                        print("[BackendManager] Wake command detected")
                        self.is_sleeping = False
                        self.chat_response.emit("Hello! I'm awake and ready to help you.")
                        self.status_update.emit("Awake and ready...")
                        self._speak_response("Hello! I'm awake and ready to help you.")
                        if hasattr(self, 'current_state'):
                            self.current_state = 'idle'
                        return
                    else:
                        print("[BackendManager] Already awake")
                        return
                
                # If sleeping, don't process any other commands except wake up
                if self.is_sleeping:
                    print(f"[BackendManager] Ignoring command while sleeping: {user_input}")
                    return
                
                # Check for interruption keywords
                if self.check_for_interruption(user_input):
                    print("[BackendManager] Interruption detected")
                    self.stop_tts()
                    self.status_update.emit("Stopped by user")
                    if hasattr(self, 'current_state'):
                        self.current_state = 'idle'
                    # Don't return here, continue processing the command if it's not just an interruption
                    # Only return if it's just an interruption command
                    if user_input.lower().strip() in ['stop', 'jarvis', 'assistant', 'halt', 'pause']:
                        return
                
                # Use the decision-making system
                decision = self.FirstLayerDMM(user_input)
                print(f"[BackendManager] Decision: {decision}")
                
                # Process based on decision
                response = self._execute_decision(user_input, decision)
                
                if response and self.is_running:
                    self.chat_response.emit(response)
                    self.status_update.emit("Available...")
                    if hasattr(self, 'current_state'):
                        self.current_state = 'idle'
                
            except Exception as e:
                print(f"[BackendManager] Error processing input: {e}")
                self.error_occurred.emit(f"Processing error: {e}")
                self.status_update.emit("Error occurred")
                if hasattr(self, 'current_state'):
                    self.current_state = 'idle'
    
    def _execute_decision(self, user_input, decision):
        """Execute the decision from the decision-making system"""
        decision_str = str(decision).lower()
        
        try:
            # Check for exit commands in decision
            if "exit" in decision_str and any(keyword in user_input.lower() for keyword in ['bye', 'goodbye', 'exit', 'quit', 'close']):
                print("[BackendManager] Exit command detected in decision")
                self.chat_response.emit("Goodbye! Closing the application...")
                self.status_update.emit("Closing...")
                # Stop all operations
                self.is_running = False
                self.stop_tts()
                # Emit exit signal to close application
                self.exitRequested.emit()
                return "EXIT"
            
            # Check for close commands FIRST (before anything else)
            if any(keyword in user_input.lower() for keyword in ["close", "exit", "quit", "stop"]):
                print("[BackendManager] Processing as close command")
                self.status_update.emit("Closing application...")
                import asyncio
                try:
                    # Extract the app name to close
                    app_to_close = self._extract_app_to_close(user_input)
                    print(f"[BackendManager] Closing: {app_to_close}")
                    
                    result = asyncio.run(self.Automation([f"close {app_to_close}"]))
                    if result:
                        response = f"Closed {app_to_close} successfully"
                    else:
                        response = f"Could not close {app_to_close}"
                    self._speak_response(response)
                    return response
                except Exception as e:
                    error_msg = f"Failed to close application: {e}"
                    print(f"[BackendManager] {error_msg}")
                    return error_msg
            
            # Check for image generation first
            if any(keyword in user_input.lower() for keyword in ["generate", "create", "make"]) and any(keyword in user_input.lower() for keyword in ["image", "picture", "photo"]):
                print("[BackendManager] Processing as image generation")
                self.status_update.emit("Generating image...")
                try:
                    self.GenerateImages(user_input)
                    response = f"Image generated for: {user_input}"
                    self._speak_response(response)
                    return response
                except Exception as e:
                    error_msg = f"Image generation failed: {e}"
                    print(f"[BackendManager] {error_msg}")
                    return error_msg
            
            # Check for automation commands
            elif any(keyword in user_input.lower() for keyword in ["open", "play", "search", "mute", "unmute", "volume"]):
                print("[BackendManager] Processing as automation task")
                self.status_update.emit("Automating...")
                import asyncio
                try:
                    # Format the command properly for automation
                    formatted_command = self._format_automation_command(user_input)
                    print(f"[BackendManager] Formatted automation command: {formatted_command}")
                    
                    result = asyncio.run(self.Automation([formatted_command]))
                    if not result:
                        self.error_occurred.emit(f"Automation failed for: {user_input}")
                    response = f"Automation task completed: {user_input}"
                    self._speak_response(response)
                    return response
                except Exception as e:
                    error_msg = f"Automation failed: {e}"
                    print(f"[BackendManager] {error_msg}")
                    self.error_occurred.emit(error_msg)
                    return error_msg
            
            elif "general" in decision_str:
                print("[BackendManager] Processing as general conversation")
                response = self.ChatBot(user_input)
                self._speak_response(response)
                return response
                
            elif "search" in decision_str or "google" in decision_str:
                print("[BackendManager] Processing as search query")
                self.status_update.emit("Searching...")
                response = self.RealtimeSearchEngine(user_input)
                self._speak_response(response)
                return response
                
            elif "automation" in decision_str:
                print("[BackendManager] Processing as automation task")
                self.status_update.emit("Automating...")
                import asyncio
                try:
                    # Format the command properly for automation
                    formatted_command = self._format_automation_command(user_input)
                    print(f"[BackendManager] Formatted automation command: {formatted_command}")
                    
                    result = asyncio.run(self.Automation([formatted_command]))
                    if not result:
                        self.error_occurred.emit(f"Automation failed for: {user_input}")
                    response = f"Automation task completed: {user_input}"
                    self._speak_response(response)
                    return response
                except Exception as e:
                    error_msg = f"Automation failed: {e}"
                    print(f"[BackendManager] {error_msg}")
                    self.error_occurred.emit(error_msg)
                    return error_msg
                    
            elif "image" in decision_str or "generate" in decision_str:
                print("[BackendManager] Processing as image generation")
                self.status_update.emit("Generating image...")
                try:
                    self.GenerateImages(user_input)
                    response = f"Image generated for: {user_input}"
                    self._speak_response(response)
                    return response
                except Exception as e:
                    error_msg = f"Image generation failed: {e}"
                    print(f"[BackendManager] {error_msg}")
                    return error_msg
                    
            else:
                print("[BackendManager] Processing as default chatbot")
                response = self.ChatBot(user_input)
                self._speak_response(response)
                return response
                
        except Exception as e:
            print(f"[BackendManager] Error in decision execution: {e}")
            return f"Error processing request: {e}"
    
    def _format_automation_command(self, user_input):
        """Format user input into proper automation command"""
        input_lower = user_input.lower().strip()
        
        print(f"[BackendManager] Formatting command: '{user_input}' -> '{input_lower}'")
        
        # Handle close commands
        if any(keyword in input_lower for keyword in ["close", "exit", "quit", "stop"]):
            app_name = self._extract_app_to_close(user_input)
            return f"close {app_name}"
        
        # Handle open commands
        if "open" in input_lower:
            # Extract the app/website name after "open"
            parts = input_lower.split("open", 1)
            if len(parts) > 1:
                app_name = parts[1].strip()
                # Remove punctuation and extra words
                app_name = app_name.rstrip('?.,!').strip()
                # Remove common filler words
                for filler in ['can you', 'please', 'for me']:
                    app_name = app_name.replace(filler, '').strip()
                print(f"[BackendManager] Extracted app name: '{app_name}'")
                return f"open {app_name}"
        
        # Handle play commands - be more specific
        if "play" in input_lower and not any(keyword in input_lower for keyword in ["generate", "create", "make", "image", "picture", "photo"]):
            parts = input_lower.split("play", 1)
            if len(parts) > 1:
                query = parts[1].strip()
                query = query.rstrip('?.,!').strip()
                # Remove common filler words
                for filler in ['can you', 'please', 'for me', 'the', 'a', 'an']:
                    query = query.replace(filler, '').strip()
                return f"play {query}"
        
        # Handle search commands
        if "search" in input_lower:
            if "youtube" in input_lower:
                parts = input_lower.split("search", 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    query = query.rstrip('?.,!').strip()
                    return f"youtube search {query}"
            else:
                parts = input_lower.split("search", 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    query = query.rstrip('?.,!').strip()
                    return f"google search {query}"
        
        # Handle system commands
        if any(cmd in input_lower for cmd in ["mute", "unmute", "volume up", "volume down"]):
            for cmd in ["mute", "unmute", "volume up", "volume down"]:
                if cmd in input_lower:
                    return f"system {cmd}"
        
        # Default: return as is
        return user_input
    
    def _speak_response(self, text):
        """Speak the response using TTS"""
        # Stop any current TTS
        self.stop_tts()
        
        # Update current state for volume simulation
        if hasattr(self, 'current_state'):
            self.current_state = 'speaking'
        
        # Emit speaking status for blob animation
        self.status_update.emit("Speaking...")
        
        # Start new TTS in separate thread
        def speak_thread():
            try:
                self.TextToSpeech(text)
                # Reset state after speaking
                if hasattr(self, 'current_state'):
                    self.current_state = 'idle'
                # Emit available status after speaking
                self.status_update.emit("Available...")
            except Exception as e:
                print(f"[BackendManager] TTS error: {e}")
                if hasattr(self, 'current_state'):
                    self.current_state = 'idle'
                self.status_update.emit("Error occurred")
        
        self.current_tts_thread = threading.Thread(target=speak_thread, daemon=True)
        self.current_tts_thread.start()
        
        print(f"[BackendManager] Started speaking: {text[:50]}...")
    
    def start_voice_listening(self):
        """Start continuous voice listening in a separate thread"""
        if not self.is_running:
            return
        
        def listen_thread():
            while self.is_running:
                try:
                    # Update status based on sleep state
                    if self.is_sleeping:
                        self.status_update.emit("Sleeping...")
                        if hasattr(self, 'current_state'):
                            self.current_state = 'sleeping'
                    else:
                        self.status_update.emit("Listening...")
                        if hasattr(self, 'current_state'):
                            self.current_state = 'listening'
                    
                    voice_input = self.SpeechRecognition()
                    
                    if voice_input and self.is_running:
                        print(f"[BackendManager] Voice input received: {voice_input}")
                        self.voice_input.emit(voice_input)
                        
                        # Check for wake command first (even when sleeping)
                        command = voice_input.lower().strip()
                        # Remove punctuation and common words for more flexible matching
                        clean_command = command.rstrip('.,!?').strip()
                        print(f"[BackendManager] Checking wake command: '{clean_command}'")
                        
                        # Check if the command contains wake keywords (including common misheard variations)
                        wake_keywords = [
                            'wake up jarvis', 'jarvis wake up', 'wake up', 'wake',
                            'wake jarvis', 'jarvis wake',           # Shorter version
                            'wake up please', 'wake please',        # With please
                            'get up jarvis', 'jarvis get up', 'get up',  # Alternative wake commands
                            'rise jarvis', 'jarvis rise', 'rise'    # Another alternative
                        ]
                        is_wake_command = any(keyword in clean_command for keyword in wake_keywords)
                        
                        if is_wake_command:
                            print(f"[BackendManager] Wake command match found!")
                            if self.is_sleeping:
                                print("[BackendManager] Wake command detected while sleeping")
                                self.is_sleeping = False
                                self.chat_response.emit("Hello! I'm awake and ready to help you.")
                                self.status_update.emit("Awake and ready...")
                                self._speak_response("Hello! I'm awake and ready to help you.")
                                if hasattr(self, 'current_state'):
                                    self.current_state = 'idle'
                            else:
                                print("[BackendManager] Already awake")
                            continue  # Skip further processing
                        
                        # If sleeping, don't process any other commands
                        if self.is_sleeping:
                            print(f"[BackendManager] Ignoring command while sleeping: {voice_input}")
                            continue
                        
                        # Process the voice input normally when awake
                        print(f"[BackendManager] Processing voice input normally: {voice_input}")
                        self.process_input(voice_input, "voice")
                    
                    # Brief pause to prevent excessive CPU usage
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"[BackendManager] Voice listening error: {e}")
                    if hasattr(self, 'current_state'):
                        self.current_state = 'idle'
                    time.sleep(1)  # Wait before retrying
        
        self.stt_thread = threading.Thread(target=listen_thread, daemon=True)
        self.stt_thread.start()
        print("[BackendManager] Voice listening started")
    
    def stop(self):
        """Stop all backend operations"""
        print("[BackendManager] Stopping backend manager...")
        self.is_running = False
        self.stop_tts()
        
        # Stop volume detection
        if hasattr(self, 'volume_timer'):
            self.volume_timer.stop()
        try:
            from Backend.VolumeDetector import stop_volume_detection
            stop_volume_detection()
        except Exception as e:
            print(f"[BackendManager] Error stopping volume detection: {e}")
        
        if self.current_tts_thread:
            self.current_tts_thread.join(timeout=1)
        
        if self.stt_thread:
            self.stt_thread.join(timeout=1)
        
        print("[BackendManager] Backend manager stopped")

    def _extract_app_to_close(self, user_input):
        """Extract the application name to close from user input"""
        input_lower = user_input.lower().strip()
        
        # Handle specific cases first - these are exact matches
        if "youtube" in input_lower:
            return "youtube"
        elif "chrome" in input_lower or "browser" in input_lower:
            return "chrome"
        
        # For other apps, find the word after close/exit/quit/stop
        for action in ["close", "exit", "quit", "stop"]:
            if action in input_lower:
                # Split by the action word and take what comes after
                parts = input_lower.split(action, 1)
                if len(parts) > 1:
                    app_name = parts[1].strip()
                    # Clean up the app name
                    app_name = app_name.rstrip('?.,!').strip()
                    # Remove common filler words but preserve the main app name
                    words = app_name.split()
                    filtered_words = []
                    for word in words:
                        if word not in ["can", "you", "please", "for", "me", "the", "a", "an"]:
                            filtered_words.append(word)
                    return " ".join(filtered_words)
        
        # If no action word found, try to extract the last meaningful word
        words = input_lower.split()
        for word in reversed(words):
            if word not in ["close", "exit", "quit", "stop", "can", "you", "please", "for", "me", "the", "a", "an", "?"]:
                return word.rstrip('.,!')
        
        return "unknown"

def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("JARVIS AI Assistant")
        app.setApplicationVersion("1.0")
        backend_manager = BackendManager()
        # Create both windows
        blob_window = BlobHomeWindow(backend_manager)
        chat_window = ChatWindow(backend_manager)
        # Cross-link windows for navigation
        blob_window.set_chat_window(chat_window)
        chat_window.set_blob_window(blob_window)
        # Show only the blob home window at start
        blob_window.show()
        # Connect backend signals for window switching
        def handle_window_switch(user_input, input_type="text"):
            if user_input.lower().strip() in ["show chat", "go to chat", "chat screen", "open chat"]:
                blob_window.hide()
                chat_window.show()
            elif user_input.lower().strip() in ["go home", "home", "show home", "blob home"]:
                chat_window.hide()
                blob_window.show()
        backend_manager.voice_input.connect(lambda text: handle_window_switch(text, "voice"))
        # Also allow switching via text input
        backend_manager.chat_response.connect(lambda text: handle_window_switch(text, "text"))
        backend_manager.exitRequested.connect(app.quit)
        backend_manager.start_voice_listening()
        print("[Main] JARVIS AI Assistant started successfully!")
        print("[Main] Voice commands and text input are ready!")
        exit_code = app.exec_()
        backend_manager.stop()
        print("[Main] Application closed successfully")
        return exit_code
    except Exception as e:
        print(f"[Main] Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

