import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from datetime import datetime, timedelta
import movingpandas as mpd
import glob


def import_data(data_directory_path):
    all_files = glob.glob(data_directory_path + "/*.csv")

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0, sep=";")
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)


    # clean data
    df = df[(df.satcount != 0)]
    df['t'] = pd.to_datetime(df['UTC_datetime'], format='%d.%m.%Y %H:%M')
    df = df.drop(columns=['datatype', 'UTC_datetime', 'UTC_date', 'satcount', 'U_bat_mV', 'bat_soc_pct', 'solar_I_mA', 'hdop', 'mag_x',	'mag_y', 'mag_z', 'acc_x','acc_y','acc_z'])
    df = df.set_index('t').tz_localize(None)
    df = df.sort_values(by=['t'])
    df = GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs=4326)

    return df

def get_trajectory_collection(df):
    return mpd.TrajectoryCollection(df, 'device_id', t='t')

def get_device_ids(df):
    return df.device_id.unique()
