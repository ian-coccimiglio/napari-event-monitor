import napari
import numpy as np
from collections import deque
from magicgui.widgets import (
    Container,
    TextEdit,
    Checkbox,
    Table,
)
from datetime import datetime


class EventMonitor(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        """
        Initializes the event monitor

        Args:
            viewer (_type_): The viewer to attach the monitor to
        """
        super().__init__(label=False)  # Initialize the Container first

        self.RECENT_LENGTH = 10
        self._viewer = viewer
        self.event_log = []
        self.recent_events = deque(maxlen=self.RECENT_LENGTH)
        self.tablewidget = Table(value=list(self.recent_events))
        self.event_attributes_list = deque(maxlen=self.RECENT_LENGTH)
        selection_event = self.tablewidget.native.selectionModel()
        selection_event.currentChanged.connect(self._view_attributes) 
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
        self._monitor_object_events(self._viewer, "viewer")
        self._monitor_object_events(self._viewer.camera, "viewer.camera")

        # Monitor layer events
        self._monitor_object_events(self._viewer.layers, "layers")

        # Monitor individual layers as they're added
        self._viewer.layers.events.inserted.connect(self._on_layer_added)

        # Monitor mouse events
        self._viewer.mouse_drag_callbacks.append(self._log_mouse_event)
        self._viewer.mouse_move_callbacks.append(self._log_mouse_event)
        self._viewer.mouse_wheel_callbacks.append(self._log_mouse_event)

    def _monitor_object_events(self, obj, event_monitor):
        """
        Cycles through an EventGroup and attaches events,
        pinging on interaction.

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

    def _view_attributes(self, current):
        if current.isValid():
            row_index = current.row()
            self.textwidget.set_value(self.event_attributes_list[row_index])
        else:
            self.textwidget.set_value("")

    def record_event_attributes(self, event, event_string):
        event_attributes = []
        event_attributes.append(f"<b><u>{event_string}</b></u>")
        for attr in dir(event):
            if not attr.startswith("_"):
                attribute_string = f"event.{attr} = {getattr(event, attr)}"
                if len(attribute_string) > 100:
                    attribute_string = f"event.{attr} = output too long"
                event_attributes.append(attribute_string)
        event_attributes_string = "<br>".join(event_attributes)
        self.event_attributes_list.append(event_attributes_string)

    def record_event_data(self, log, event_string, event=None):
        event_time = datetime.now().strftime(format="%H:%M:%S.%f")[:-3]
        log.append({"Event": event_string.split(".")[-1],
                    "Time": event_time,
                    "API": event_string})
        if event is not None:
            self.record_event_attributes(event, event_string)

    def get_event_string(self, event_monitor, event_name):
        return f"{event_monitor}.events.{event_name}"

    def _log_mouse_event(self, a, event):
        self._log_event(event, f"{event.type}")

    def _on_layer_added(self, event):
        layer = event.value
        self._monitor_object_events(layer, "viewer."+event.value._name)


# Usage
if __name__ == "__main__":
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
