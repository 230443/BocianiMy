import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from datetime import timedelta
import movingpandas as mpd
import glob
import corine_service as cs


def import_data(data_directory_path):
    all_files = glob.glob(data_directory_path + "/*.csv")

    li = []

    if len(all_files) == 0:
        return None

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0, sep=";")
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)

    # clean data
    df = df[(df.satcount != 0)]
    df["t"] = pd.to_datetime(df["UTC_datetime"], format="%d.%m.%Y %H:%M")
    df = df.drop(
        columns=[
            "datatype",
            "UTC_time",
            "UTC_date",
            "satcount",
            "U_bat_mV",
            "bat_soc_pct",
            "solar_I_mA",
            "hdop",
            "mag_x",
            "mag_y",
            "mag_z",
            "acc_x",
            "acc_y",
            "acc_z",
        ]
    )
    df = df.set_index("t").tz_localize(None)
    df = df.sort_values(by=["t"])
    df = GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs=4326
    )

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
