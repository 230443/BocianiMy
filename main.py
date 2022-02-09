import PySimpleGUI as sg
import geoanalysis as g
import pandas as pd

# sg.theme("DarkAmber")

df = pd.DataFrame([])
tc = []

layout = [
    [sg.Text("Folder z plikami csv")],
    [sg.Input(key="dirname", default_text="data"), sg.FolderBrowse()],
    [sg.Button("Otwórz"), sg.Button("Anuluj")],
    [
        sg.Table(
            values=df,
            headings=[
                "device_id",
                "UTC_datetime",
                "Latitude",
                "Longitude",
                "Altitude_m",
                "speed_km_h",
                "direction_deg",
                "temperature_C",
            ],
            vertical_scroll_only=False,
            visible=False,
            key="-PREVIEW_TABLE-",
        ),
        sg.Listbox(
            values=[],
            size=(30, 6),
            select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
            visible=False,
            key="deviceIdListbox",
        ),
    ],
    [
        sg.Text("Średnica obszaru:", size=20),
        sg.Input(
            key="-MAX_DIAMETER-",
            default_text=10000,
            size=6,
            justification="right",
            enable_events=True,
        ),
        sg.Text("m"),
    ],
    [
        sg.Text("Minimalny czas postoju:", size=20),
        sg.Input(
            key="-MIN_DURATION-",
            default_text=48,
            size=6,
            justification="right",
            enable_events=True,
        ),
        sg.Text("h"),
    ],
    [
        sg.Button("Znajdź przystanki", key="stopDetect", disabled=True),
    ],
    [
        sg.Table(
            values=df,
            headings=[
                "geometry",
                "start_time",
                "end_time",
                "traj_id",
                "duration_h",
                "corine_label_id",
                "corine_label_text",
            ],
            vertical_scroll_only=False,
            visible=False,
            key="-STOPS_TABLE-",
        ),
    ],
]


def main():
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
            print(df.columns)
            df = g.import_data(data_directory_path=values["dirname"])
            window["-PREVIEW_TABLE-"].update(
                visible=True,
                values=df.values.tolist(),
            )
            window["deviceIdListbox"].update(visible=True, values=g.get_device_ids(df))
            window["stopDetect"].update(disabled=False)

        if event == "stopDetect":
            window["-PREVIEW_TABLE-"].update(
                values=df[df["device_id"].isin(values["deviceIdListbox"])].values.tolist(),
            )
            filtered_df = df[df["device_id"].isin(list(values["deviceIdListbox"]))]
            tc = g.get_trajectory_collection(filtered_df)
            stops = g.detect_stops(
                tc,
                min_duration_h=int(values["-MIN_DURATION-"]),
                max_diameter=int(values["-MAX_DIAMETER-"]),
            )
            window["-STOPS_TABLE-"].update(visible=True, values=stops.values.tolist())

        # if (
        #     event == "-MAX_DIAMETER-"
        #     and values["-MAX_DIAMETER-"]
        #     and values["-MAX_DIAMETER-"][-1] not in ("0123456789")
        # ):
        #     window["-MAX_DIAMETER-"].update(values["-MAX_DIAMETER-"][:-1])
        # if (
        #     event == "-MIN_DURATION-"
        #     and values["-MIN_DURATION-"]
        #     and values["-MIN_DURATION-"][-1] not in ("0123456789")
        # ):
        #     window["-MIN_DURATION-"].update(values["-MIN_DURATION-"][:-1])


    window.close()
    exit(0)


if __name__ == '__main__':
    sg.theme('black')
    main()
