import requests
import json
from math import cos

URL = "https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/identify"
BASE_PARAMS = {
    "geometryType": "esriGeometryPoint",
    "sr": "4326",
    "tolerance": "10",
    "imageDisplay": "10,10,96",
    "returnGeometry": "false",
    "f": "json",
}


def get_corine_data(x, y, diameter=10000):
    payload = BASE_PARAMS

    map_extend_y = 110574 / diameter / 2
    map_extend_x = 111320 * cos(x) / diameter / 2

    mapExtend = ",".join(
        (
            str(y - map_extend_y),
            str(x - map_extend_x),
            str(y + map_extend_y),
            str(x + map_extend_x),
        )
    )
    payload["mapExtent"] = mapExtend
    payload["geometry"] = ",".join((str(y), str(x)))

    response = requests.get(URL, params=payload)
    try:
        attributes = response.json()["results"][0]["attributes"]
    except IndexError as e:
        return "", ""
    return (attributes["LABEL3"], attributes["CODE_18"])
