"""Microphone recorder with GObject signal bridge."""

import threading
import queue

import numpy as np
import pyaudio
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GObject, GLib


SAMPLE_RATE = 44100
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1


class Recorder(GObject.Object):
    """Trådad mikrofon-inspelning med PyAudio.

    Emitterar GObject-signaler på huvudtråden via GLib.idle_add().
    """

    __gsignals__ = {
        "audio-chunk-ready": (GObject.SignalFlags.RUN_LAST, None, (object,)),
        "recording-started": (GObject.SignalFlags.RUN_LAST, None, ()),
        "recording-stopped": (GObject.SignalFlags.RUN_LAST, None, ()),
        "recording-complete": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object, int),
        ),
    }

    def __init__(self, sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._recording = False
        self._thread = None
        self._queue = queue.Queue()
        self._chunks = []

    @property
    def is_recording(self):
        return self._recording

    def start_recording(self):
        """Starta inspelning i en bakgrundstråd."""
        if self._recording:
            return
        self._recording = True
        self._chunks = []
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        GLib.idle_add(self.emit, "recording-started")

    def stop_recording(self):
        """Stoppa inspelning och emittera komplett ljud."""
        if not self._recording:
            return
        self._recording = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _record_loop(self):
        """Bakgrundstråd: läs ljud från mikrofon."""
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            while self._recording:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                self._chunks.append(chunk)
                GLib.idle_add(self._emit_chunk, chunk)

            stream.stop_stream()
            stream.close()
        finally:
            pa.terminate()

        # Emit complete recording on main thread
        if self._chunks:
            full_audio = np.concatenate(self._chunks)
            GLib.idle_add(self._emit_complete, full_audio)

    def _emit_chunk(self, chunk):
        self.emit("audio-chunk-ready", chunk)
        return False  # Don't repeat

    def _emit_complete(self, audio):
        self.emit("recording-stopped")
        self.emit("recording-complete", audio, self.sample_rate)
        return False
