import json

import pandas as pd
import requests

from .constants import CASES_PER_TYPE


def create_case_url(kind: str, kind_type: str, case_number: int):
    if case_number > CASES_PER_TYPE[kind][kind_type]:
        raise ValueError(
            f"Case number {case_number} is not valid for {kind}{kind_type}"
        )
    base_url = "https://raw.githubusercontent.com/CervEdin/solomon-vrptw-benchmarks/main/{}/{}/{}{}{}.json"
    if case_number < 10:
        return base_url.format(kind, kind_type, kind, kind_type, f"0{case_number}")
    else:
        return base_url.format(kind, kind_type, kind, kind_type, case_number)


def create_case_urls(kind: str, kind_type: str):
    urls = []
    for i in range(1, CASES_PER_TYPE[kind][kind_type] + 1):
        urls.append(create_case_url(kind, kind_type, i))
    return urls


def download_url_json(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def parse_instance(kind: str, kind_type: str, case_number: int):
    url = create_case_url(kind, kind_type, case_number)
    data = download_url_json(url)
    instance_name = data["instance"]
    vehicle_nr = data["vehicle-nr"]
    capacity = data["capacity"]

    customers = pd.json_normalize(data["customers"])

    return instance_name, vehicle_nr, capacity, customers
