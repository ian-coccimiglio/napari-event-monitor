[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/<your-plugin-name-here>)](https://napari-hub.org/plugins/<your-plugin-name-here>)


# napari-event-monitor
Testing and documenting the napari Event Loop

## Background
Have you ever clicked a button in the napari UI and wondered: How can I trigger that programatically? If so, the napari Event Monitor may be a worthwhile tool for you!

This tool logs and reports all of the builtin napari events that are listed in the [napari Events Reference](https://napari.org/stable/guides/events_reference.html) (i.e., excluding user plugins). So object highlighting, camera moves, viewer zoom, shape manipulation, mouse drags, are just some of the examples of what will be recorded. The plugin then shows the specific API required to trigger that action.

Further, if you click on the table entries, you'll see the event attributes. For example, if you add a point, an event will be created with the attribute `added`.

You can then save the entire list of events in CSV format for further diagnostics.

## Installation

1) Either clone this directory onto your local machine within your napari environment and run
`python -m pip install -e .`

or 

2) Simply search for this package on the napari hub, and install from the GUI.

The plugin will then appear in the menus under Plugins\>Make Event Monitor 

## Usage

Simply start the plugin from the menus, open some images, and watch the 

## Contributions

Any and all contributions are welcome! Especially testing and other events.
