import pyaudio
import numpy as np
import threading
import time
import queue

class VolumeDetector:
    """Real-time microphone volume detector for blob animation"""
    
    def __init__(self, chunk_size=1024, format=pyaudio.paFloat32, channels=1, rate=44100):
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        self.volume_queue = queue.Queue(maxsize=10)
        self.current_volume = 0.0
        self.volume_thread = None
        
    def start_listening(self):
        """Start listening for microphone input"""
        if self.is_listening:
            return
            
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_listening = True
            self.volume_thread = threading.Thread(target=self._volume_loop, daemon=True)
            self.volume_thread.start()
            print("[VolumeDetector] Started listening for volume levels")
            
        except Exception as e:
            print(f"[VolumeDetector] Error starting volume detection: {e}")
    
    def stop_listening(self):
        """Stop listening for microphone input"""
        self.is_listening = False
        
        if self.volume_thread:
            self.volume_thread.join(timeout=1)
            
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        print("[VolumeDetector] Stopped listening for volume levels")
    
    def _volume_loop(self):
        """Main volume detection loop"""
        while self.is_listening:
            try:
                if self.stream:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    
                    # Calculate RMS volume
                    rms = np.sqrt(np.mean(audio_data**2))
                    
                    # Convert to a 0-1 scale with some smoothing
                    volume = min(1.0, rms * 10)  # Adjust multiplier as needed
                    
                    # Apply smoothing
                    self.current_volume = self.current_volume * 0.7 + volume * 0.3
                    
                    # Put in queue for GUI consumption
                    try:
                        self.volume_queue.put_nowait(self.current_volume)
                    except queue.Full:
                        # Remove old value and add new one
                        try:
                            self.volume_queue.get_nowait()
                            self.volume_queue.put_nowait(self.current_volume)
                        except queue.Empty:
                            pass
                            
            except Exception as e:
                print(f"[VolumeDetector] Error in volume loop: {e}")
                time.sleep(0.1)
    
    def get_current_volume(self):
        """Get the current volume level (0.0 to 1.0)"""
        return self.current_volume
    
    def get_volume_from_queue(self):
        """Get volume from queue (non-blocking)"""
        try:
            return self.volume_queue.get_nowait()
        except queue.Empty:
            return self.current_volume
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()

# Global instance for easy access
volume_detector = VolumeDetector()

def get_volume_level():
    """Get current volume level for external use"""
    return volume_detector.get_current_volume()

def start_volume_detection():
    """Start volume detection"""
    volume_detector.start_listening()

def stop_volume_detection():
    """Stop volume detection"""
    volume_detector.stop_listening()

if __name__ == "__main__":
    # Test the volume detector
    try:
        start_volume_detection()
        print("Volume detection started. Press Ctrl+C to stop.")
        
        while True:
            volume = get_volume_level()
            print(f"Volume: {volume:.3f}")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping volume detection...")
        stop_volume_detection()
        volume_detector.cleanup() 