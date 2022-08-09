import requests
from contextlib import closing
import csv
import json_stream.requests
from dash import html
import numpy as np
import dash_mantine_components as dmc


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


# ! Not used for now
def create_table_from_df(df):
    # Convert df to html table
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]

    # Convert html table to mantine dash component
    table_mantine = dmc.Table(striped=True, highlightOnHover=True, children=table)

    return table_mantine


def create_table_csv(url, n_rows=10):
    rows = []
    header = []
    with closing(requests.get(url, stream=True)) as r:
        f = (line.decode("utf-8") for line in r.iter_lines())
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for idx, l_row in enumerate(reader):
            if idx == 0:
                header = [html.Tr([html.Th(col) for col in l_row])]
            else:
                rows += [html.Tr([html.Td(cell) for cell in l_row])]
            if idx > n_rows:
                break

    table = [html.Thead(header), html.Tbody(rows)]
    return dmc.Table(striped=True, highlightOnHover=True, children=table)
