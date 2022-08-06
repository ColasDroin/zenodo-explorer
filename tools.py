import requests
from contextlib import closing
import csv
import json_stream.requests
from dash import html
import numpy as np


def return_dataset_json(url_zenodo):
    # Transform URL for API request
    record_id = url_zenodo.split("/")[-1]
    url = "https://zenodo.org/api/records/" + record_id

    try:
        r = requests.get(url, timeout=2)  # timeout in seconds
    except requests.exceptions.ConnectTimeout:
        print("Connection error")

    if not r.ok:
        print("DOI could not be resolved. Try again, or use a different URL.")
    else:
        return r.json()


def return_dataset_info(json_data):
    dic_metadata = {}
    dic_metadata["Title"] = "Title: {}".format(json_data["metadata"]["title"])
    dic_metadata["Keywords"] = "Keywords: " + ", ".join(json_data["metadata"].get("keywords", []))
    dic_metadata["Publication date"] = (
        "Publication date: " + json_data["metadata"]["publication_date"]
    )
    dic_metadata["DOI"] = "DOI: " + json_data["metadata"]["doi"]
    dic_metadata["Total size"] = "Total size: {:.1f} MB".format(
        sum(f["size"] for f in json_data["files"]) / 1024**2
    )
    return dic_metadata


def return_dataset_files(json_data, url_zenodo):
    record_id = url_zenodo.split("/")[-1]
    files = json_data["files"]
    l_names = []
    l_links = []
    l_sizes = []
    for f in files:
        l_names.append(f["key"])
        l_links.append(
            "https://zenodo.org/record/{}/files/{}".format(record_id, l_names[-1]).replace(
                " ", "%20"
            )
        )
        # log_scale where 10**4, i.e. 10GB is max size
        l_sizes.append(np.log10(f["size"] / 1024**2))
    return l_names, l_links, l_sizes
