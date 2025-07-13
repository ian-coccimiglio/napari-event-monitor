#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 22:30:48 2025

@author: iancoccimiglio
"""

import napari
import numpy as np
from collections import deque

# from qtpy.QtWidgets import QTextBrowser, QWidget
from magicgui.widgets import (
    Container,
    TextEdit,
    Checkbox,
    Table,
)
from datetime import datetime
from napari.settings import get_settings
get_settings().application.ipy_interactive = False

class EventMonitor(Container):
    def __init__(self, viewer):
        """
        Initializes the event monitor

        Args:
            viewer (_type_): The viewer to attach the monitor to
        """
        super().__init__(label=False)  # We need to initialize the Container first.

        self.RECENT_LENGTH = 10
        
        self.viewer = viewer
        self.event_log = []
        self.recent_events = deque(maxlen=self.RECENT_LENGTH)
        self.tablewidget = Table(value=list(self.recent_events))
        self.event_attributes_list = deque(maxlen=self.RECENT_LENGTH)
        self.tablewidget.native.cellClicked.connect(self._view_attributes)
        self.mouse_events_checkbox = Checkbox(label="Mouse Events")
        self.status_events_checkbox = Checkbox(label="Status Events")
        self.textwidget = TextEdit(value="")
        self.extend([self.tablewidget,
                     self.mouse_events_checkbox,
                     self.status_events_checkbox,
                     self.textwidget])
        self.setup_monitoring()

    def setup_monitoring(self):
        # Monitor viewer events
        self._monitor_object_events(self.viewer, "viewer")
        self._monitor_object_events(self.viewer.camera, "viewer.camera")

        # Monitor layer events
        self._monitor_object_events(self.viewer.layers, "layers")

        # Monitor individual layers as they're added
        self.viewer.layers.events.inserted.connect(self._on_layer_added)

        # Monitor mouse events
        self.viewer.mouse_drag_callbacks.append(self._log_mouse_event)
        self.viewer.mouse_move_callbacks.append(self._log_mouse_event)
        self.viewer.mouse_wheel_callbacks.append(self._log_mouse_event)

    def _monitor_object_events(self, obj, event_monitor):
        """
        Cycles through an EventGroup and attaches events which ping on interaction.

        Parameters
        ----------
        obj : TYPE
            DESCRIPTION.
        event_monitor : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if hasattr(obj, "events"):
            for event_name in obj.events:
                event = getattr(obj.events, event_name)
                event_string = self.get_event_string(event_monitor, event_name)
                event.connect(
                    lambda e, en=event_string: self._log_event(e, en)
                )
                # getting class name - .__cls__.name

    def _log_event(self, event, event_string):
        mouse_events_disabled = not self.mouse_events_checkbox.get_value()
        status_events_disabled = not self.status_events_checkbox.get_value()
        if ("mouse" in event_string and mouse_events_disabled):
            return
        if ("status" in event_string and status_events_disabled):
            return
        self.record_event_data(self.event_log, event_string)
        self.record_event_data(self.recent_events, event_string, event=event)
        self.tablewidget.set_value(list(self.recent_events))
        if len(self.event_log) >= self.RECENT_LENGTH:
            recent_range = range(len(self.event_log)-self.RECENT_LENGTH,
                                 len(self.event_log))
            indices = list(recent_range)
            self.tablewidget.row_headers = indices
        self.tablewidget.native.scrollToBottom()

    def _view_attributes(self, index):
        self.textwidget.set_value(self.event_attributes_list[index])

    def record_event_attributes(self, event):
        event_attributes = ''
        for attr in dir(event):
            if not attr.startswith("_"):
                attribute_string = f"{attr} = {getattr(event, attr)}\n"
                if len(attribute_string) > 100:
                    attribute_string = f"{attr} = output too long\n"
                event_attributes = event_attributes + attribute_string
        self.event_attributes_list.append(event_attributes)

    def record_event_data(self, log, event_string, event=None):
        event_time = datetime.now().strftime(format="%H:%M:%S.%f")[:-3]
        log.append({"Event": event_string.split(".")[-1],
                    "Time": event_time,
                    "API": event_string})
        if event is not None:
            self.record_event_attributes(event)

    def get_event_string(self, event_monitor, event_name):
        return f"{event_monitor}.events.{event_name}"

    def _log_mouse_event(self, a, event):
        self._log_event(event, f"{event.type}")

    def _on_layer_added(self, event):
        layer = event.value
        self._monitor_object_events(layer, "layer")


# Usage
viewer = napari.Viewer()
monitor = EventMonitor(viewer)
viewer.window.add_dock_widget(monitor)

features = {"confidence": np.array([1])}

text = {
    "string": "Confidence is {confidence:.2f}",
    "size": 20,
    "color": "blue",
    "translation": np.array([-30, 0]),
}

viewer.add_image(np.random.random((100, 100)))
viewer.add_points([0, 10], features=features, text=text)
napari.run()
