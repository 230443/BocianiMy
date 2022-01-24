import requests
from math import cos
from collections import Counter

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

    payload["mapExtent"] = ",".join([str(i) for i in get_envelope(x, y, diameter)])
    payload["geometry"] = ",".join((str(x), str(y)))

    response = requests.get(URL, params=payload)

    result = ()

    try:
        attributes = response.json()["results"][0]["attributes"]
        result = (
            attributes["CODE_18"],
            attributes["LABEL3"],
        )
    except Exception:
        result = (None, None)
    return result


def get_envelope(x, y, diameter=10000):
    map_extend_y = (diameter / 110574) / 2
    map_extend_x = (diameter / (111320 * cos(x))) / 2
    return (
        x - map_extend_x,
        y - map_extend_y,
        x + map_extend_x,
        y + map_extend_y,
    )


def get_corine_data_list(x, y, diameter=10000):

    results = []

    for dia in [diameter / 10, diameter / 3, diameter / 3 * 2]:
        a, b, c, d = get_envelope(x, y, dia)
        r = [
            get_corine_data(a, b, dia),
            get_corine_data(c, d, dia),
            get_corine_data(a, d, dia),
            get_corine_data(c, b, dia),
            get_corine_data(x, b, dia),
            get_corine_data(x, d, dia),
            get_corine_data(a, y, dia),
            get_corine_data(c, y, dia),
        ]

        results.extend(r)

    results.append(get_corine_data(x, y))

    return results


def get_corine_data_types(x, y, diameter=10000):

    l = get_corine_data_list(x, y, diameter)
    if l[0] == None:
        return ""

    return ",".join([x[1] for x in set(l)])


def get_latest_corine_label(x, y, diameter=10000):
    l = get_corine_data_list(x, y, diameter)

    max_no_500_key = 0
    label = ""

    for k, v in l:
        if k is None:
            return ""
        k = int(k)
        if k > max_no_500_key and k < 500:
            max_no_500_key = k
            label = v

    return label
