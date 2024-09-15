import json
import os

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


def save_json_to_file(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


def load_json_from_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def parse_instance(kind: str, kind_type: str, case_number: int):
    data_dir = "./local_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    file_path = os.path.join(data_dir, f"{kind}_{kind_type}_{case_number}.json")
    
    if os.path.exists(file_path):
        data = load_json_from_file(file_path)
    else:
        url = create_case_url(kind, kind_type, case_number)
        data = download_url_json(url)
        if data is not None:
            save_json_to_file(data, file_path)
        else:
            raise ValueError(f"Failed to download data for {kind} {kind_type} {case_number}")

    instance_name = data["instance"]
    vehicle_nr = data["vehicle-nr"]
    capacity = data["capacity"]

    customers = pd.json_normalize(data["customers"])

    return instance_name, vehicle_nr, capacity, customers
