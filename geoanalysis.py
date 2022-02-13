import pandas as pd
from geopandas import GeoDataFrame, points_from_xy
from datetime import timedelta
import movingpandas as mpd
import corine_service as cs
from os import path


colums_mapper = {
    "S/N": "device_id",
    "Longtitude": "Longitude",
    "GpsNumber": "device_id",
}


def import_data(file_list):

    li = []

    if len(file_list) == 0:
        return None

    for filename in file_list:
        df = pd.read_csv(filename, index_col=None, header=0, sep=None)
        df = unify_columns(df)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    df["timestamp"] = df["t"]
    df = df.set_index("t").tz_localize(None)
    df = df.sort_values(by=["t"])
    df = GeoDataFrame(df, geometry=points_from_xy(df.Longitude, df.Latitude), crs=4326)

    return df


def unify_columns(df):
    df.rename(columns=colums_mapper, inplace=True, errors="ignore")

    if "UTC_datetime" in df.columns:
        df = df[(df.satcount != 0)]
        df["t"] = pd.to_datetime(df["UTC_datetime"], format="%d.%m.%Y %H:%M", utc=True)
    if "Collecting time" in df.columns:
        df = df[(df.HDOP != 0)]
        df["t"] = pd.to_datetime(df["Collecting time"], utc=True)
    if "GPSTime" in df.columns:
        df["t"] = pd.to_datetime(df["GPSTime"], format="%d.%m.%Y %H:%M", utc=True)

    print(df)

    df = df[["t", "device_id", "Latitude", "Longitude"]]
    return df


def get_trajectory_collection(df):
    return mpd.TrajectoryCollection(df, "device_id", t="t")


def get_device_ids(df):
    return df.device_id.unique()


def detect_stops(tc, min_duration_h, max_diameter, include_corine=False):

    min_duration = timedelta(hours=min_duration_h)

    stops = mpd.TrajectoryStopDetector(tc).get_stop_points(
        min_duration=min_duration, max_diameter=max_diameter
    )
    if len(stops) != 0:
        stops = stops.assign(duration_h=stops.duration_s / (60 * 60))
        stops = stops.drop(columns=["duration_s"])
        if include_corine:
            stops = add_corine(stops)
    return stops


def add_corine(stops):
    stops[["corine_label_id", "corine_label_text"]] = stops.apply(
        lambda row: cs.get_corine_data(x=row["geometry"].x, y=row["geometry"].y),
        axis=1,
        result_type="expand",
    )
    return stops


def save_to_file(df, filename):
    driver = path.splitext(filename)[1][1:].upper()
    if driver == "GPX":
        df["ele"] = 0.0
        df["magvar"] = 0.0
        df["geoidheight"] = 0.0
        df[
            ["geometry", "ele", "start_time", "magvar", "geoidheight", "traj_id"]
        ].to_file(filename, driver=driver)
    else:
        df.to_file(filename)
