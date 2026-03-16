"""Recording controls with real-time waveform display."""

import math

import numpy as np
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, GLib, Gdk

from pronounceit.i18n import _


class RecordingView(Gtk.Box):
    """Inspelningskontroller med vågformsvisning i realtid."""

    def __init__(self, recorder, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.recorder = recorder
        self._waveform_data = np.zeros(1024)
        self._is_recording = False

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        # Waveform drawing area
        self.waveform = Gtk.DrawingArea()
        self.waveform.set_size_request(-1, 80)
        self.waveform.set_draw_func(self._draw_waveform)
        self.waveform.set_vexpand(False)
        self.append(self.waveform)

        # Button row
        button_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            halign=Gtk.Align.CENTER,
        )

        # Record button
        self.record_btn = Gtk.Button(label=_("Record"))
        self.record_btn.add_css_class("suggested-action")
        self.record_btn.add_css_class("pill")
        self.record_btn.set_size_request(140, 48)
        button_box.append(self.record_btn)

        # Stop button
        self.stop_btn = Gtk.Button(label=_("Stop"))
        self.stop_btn.add_css_class("destructive-action")
        self.stop_btn.add_css_class("pill")
        self.stop_btn.set_size_request(140, 48)
        self.stop_btn.set_sensitive(False)
        button_box.append(self.stop_btn)

        self.append(button_box)

        # Status label
        self.status_label = Gtk.Label(label=_("Press \'Record\' to start"))
        self.status_label.add_css_class("dim-label")
        self.append(self.status_label)

    def _connect_signals(self):
        self.record_btn.connect("clicked", self._on_record)
        self.stop_btn.connect("clicked", self._on_stop)
        self.recorder.connect("audio-chunk-ready", self._on_chunk)
        self.recorder.connect("recording-started", self._on_started)
        self.recorder.connect("recording-stopped", self._on_stopped)

    def _on_record(self, button):
        self.recorder.start_recording()

    def _on_stop(self, button):
        self.recorder.stop_recording()

    def _on_started(self, recorder):
        self._is_recording = True
        self.record_btn.set_sensitive(False)
        self.stop_btn.set_sensitive(True)
        self.status_label.set_label(_("Recording..."))

    def _on_stopped(self, recorder):
        self._is_recording = False
        self.record_btn.set_sensitive(True)
        self.stop_btn.set_sensitive(False)
        self.status_label.set_label(_("Recording ready! Analyzing..."))

    def _on_chunk(self, recorder, chunk):
        # Keep a rolling buffer for waveform display
        self._waveform_data = np.concatenate(
            [self._waveform_data[len(chunk):], chunk]
        )
        self.waveform.queue_draw()

    def _draw_waveform(self, area, cr, width, height):
        """Rita vågform med Cairo."""
        # Background
        cr.set_source_rgb(0.12, 0.12, 0.14)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        if len(self._waveform_data) == 0:
            return

        # Waveform
        n = len(self._waveform_data)
        mid_y = height / 2
        step = max(1, n // width)

        if self._is_recording:
            cr.set_source_rgb(0.3, 0.8, 0.4)  # Green while recording
        else:
            cr.set_source_rgb(0.4, 0.6, 0.9)  # Blue when idle

        cr.set_line_width(1.5)
        cr.move_to(0, mid_y)

        for x in range(width):
            idx = min(int(x * n / width), n - 1)
            y = mid_y - self._waveform_data[idx] * mid_y * 0.9
            cr.line_to(x, y)

        cr.stroke()

        # Center line
        cr.set_source_rgba(1, 1, 1, 0.2)
        cr.set_line_width(0.5)
        cr.move_to(0, mid_y)
        cr.line_to(width, mid_y)
        cr.stroke()
