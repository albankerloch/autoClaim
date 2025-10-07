#!/usr/bin/env python3
"""
Audio utilities for the autoClaim realtime audio application.
Provides audio constants and async audio player functionality.
"""

import asyncio
import threading
import numpy as np
from typing import Optional
import sounddevice as sd

# Audio configuration constants
CHANNELS = 1  # Mono audio
SAMPLE_RATE = 24000  # 24kHz sample rate commonly used for realtime audio


class AudioPlayerAsync:
    """
    Asynchronous audio player that can queue and play audio data.
    Designed for real-time audio streaming applications.
    """
    
    def __init__(self):
        self.audio_queue: asyncio.Queue = asyncio.Queue()
        self.is_playing = False
        self.frame_count = 0
        self.stream: Optional[sd.OutputStream] = None
        self._stop_event = threading.Event()
        
    def reset_frame_count(self) -> None:
        """Reset the frame count to zero."""
        self.frame_count = 0
        
    def add_data(self, audio_data: bytes) -> None:
        """
        Add audio data to the playback queue.
        
        Args:
            audio_data: Raw audio bytes to be played
        """
        try:
            # Convert bytes to numpy array
            # Assuming 16-bit PCM audio data
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Add to queue for playback
            asyncio.create_task(self._queue_audio(audio_float))
            
        except Exception as e:
            print(f"Error adding audio data: {e}")
    
    async def _queue_audio(self, audio_data: np.ndarray) -> None:
        """Internal method to queue audio data."""
        await self.audio_queue.put(audio_data)
        
        # Start playback if not already playing
        if not self.is_playing:
            await self.start_playback()
    
    async def start_playback(self) -> None:
        """Start the audio playback loop."""
        if self.is_playing:
            return
            
        self.is_playing = True
        
        try:
            # Create output stream
            self.stream = sd.OutputStream(
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype='float32',
                callback=self._audio_callback
            )
            
            self.stream.start()
            
            # Keep playing until stopped
            while self.is_playing and not self._stop_event.is_set():
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
        except Exception as e:
            print(f"Error in audio playback: {e}")
        finally:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            self.is_playing = False
    
    def _audio_callback(self, outdata: np.ndarray, frames: int, time, status) -> None:
        """
        Callback function for the audio stream.
        
        Args:
            outdata: Output buffer to fill with audio data
            frames: Number of frames to write
            time: Timing information
            status: Stream status
        """
        try:
            # Try to get audio data from queue (non-blocking)
            try:
                audio_chunk = self.audio_queue.get_nowait()
                
                # Ensure we don't exceed the buffer size
                frames_to_write = min(len(audio_chunk), frames)
                
                # Copy audio data to output buffer
                if len(audio_chunk.shape) == 1:  # Mono
                    outdata[:frames_to_write, 0] = audio_chunk[:frames_to_write]
                else:  # Stereo or multi-channel
                    outdata[:frames_to_write] = audio_chunk[:frames_to_write].reshape(-1, CHANNELS)
                
                # Fill remaining buffer with silence if needed
                if frames_to_write < frames:
                    outdata[frames_to_write:] = 0
                    
                self.frame_count += frames_to_write
                
            except asyncio.QueueEmpty:
                # No audio data available, output silence
                outdata.fill(0)
                
        except Exception as e:
            print(f"Error in audio callback: {e}")
            outdata.fill(0)
    
    def stop(self) -> None:
        """Stop audio playback."""
        self.is_playing = False
        self._stop_event.set()
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop()