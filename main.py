import PySimpleGUI as sg
import geoanalysis as g
import pandas as pd

# sg.theme("DarkAmber")
df = g.import_data("data")

layout = [
    [sg.Text("Folder z plikami csv")],
    [sg.Input(key="dirname"), sg.FolderBrowse()],
    [sg.Button("Otwórz"), sg.Button("Anuluj")],
    [
        sg.Table(
            values=df,
            headings=list(df.columns.values),
            visible=False,
            key="table",
        ),
        sg.Listbox(
            values=["Listbox 1", "Listbox 2", "Listbox 3"],
            size=(30, 6),
            visible=False,
            key="deviceIdListbox",
        ),
    ],
]

# Create the Window
window = sg.Window("Window Title", layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if (
        event == sg.WIN_CLOSED or event == "Cancel"
    ):  # if user closes window or clicks cancel
        break
    if event == "Otwórz" and values["dirname"] != "":
        df = g.import_data(data_directory_path=values["dirname"])
        window["table"].update(
            visible=True,
            values=list(df.values),
        )
        window["deviceIdListbox"].update(visible=True, values=g.get_device_ids(df))


window.close()
