#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 22:30:48 2025

@author: iancoccimiglio
"""

import napari
import numpy as np
from collections import defaultdict, deque

# from qtpy.QtWidgets import QTextBrowser, QWidget
from magicgui.widgets import (
    Container,
    TextEdit,
    Checkbox,
    Table
)
from datetime import datetime
from napari.settings import get_settings
get_settings().application.ipy_interactive = False

# textWidget = TextEdit(value="text edit value...", label="TextEdit:")


class EventMonitor(Container):
    def __init__(self, viewer):
        """
        Initializes the event monitor

        Args:
            viewer (_type_): The viewer to attach the monitor to
        """
        super().__init__(label=False)  # We need to initialize the Container first.
        self.viewer = viewer
        self.event_log = []
        self.recent_events = deque(maxlen=20)
        # self.event_data = defaultdict(dict)
        # self.event_data["Event"] = defaultdict(str)
        # self.event_data["Time"] = defaultdict(str)
        # self.event_data["API"] = defaultdict(str)
        # self.event_log.extend({"Event": str, "Time": str, "API": str})
        # self.recent_events.extend({"Event": str, "Time": str, "API": str})

        # self.event_data = {"Event": {"Event_1": "Opacity",
        #                              "Event_2": "Mouse_Move"},
        #                              "Time": {"Event_1": "1.2",
        #                                       "Event_2": "1.5"}}

        self.tablewidget = Table(value=list(self.recent_events))
        self.mouse_events_checkbox = Checkbox(label="Mouse Events")
        self.status_events_checkbox = Checkbox(label="Status Events")
        self.extend([self.tablewidget,
                     self.mouse_events_checkbox,
                     self.status_events_checkbox])
        # self.event_data["Event"]["Event_1"] = "A"
        # print(len(self.event_data["Event"].keys()))
        # self.tablewidget.set_value(self.event_data)
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
        self.set_event_data(event, event_string)
        self.tablewidget.set_value(list(self.recent_events))
        self.tablewidget.native.scrollToBottom()

    def set_event_data(self, event, event_string):
        event_time = datetime.now().strftime(format="%H:%M:%S.%f")[:-3]
        self.event_log.append({"Event": event_string.split(".")[-1],
                               "Time": event_time,
                               "API": event_string})
        self.recent_events.append({"Event": event_string.split(".")[-1], 
                                   "Time": event_time, 
                                   "API": event_string})
        # if hasattr(event, "type"):
        #     self.event_data["type"] = event.type
        # if hasattr(event, "action"):
        #     self.event_data["action"] = event.action

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


# napari.qt.Window.add_dock_widget(monitor)
viewer.add_image(np.random.random((100, 100)))
viewer.add_points([0, 10], features=features, text=text)
napari.run()
