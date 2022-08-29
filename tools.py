import requests
from contextlib import closing
import csv
import json_stream.requests
from dash import html, dash_table
import dash_leaflet as dl

import pandas as pd
import numpy as np
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import markdownify
from collections import OrderedDict


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


def return_dataset_description(json_data):
    h = markdownify.markdownify(json_data["metadata"]["description"], heading_style="ATX")
    return h


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


def return_table_files(json_data, url_zenodo):
    # Browse files and add to table
    record_id = url_zenodo.split("/")[-1]
    files = json_data["files"]
    l_names = []
    l_links = []
    l_size = []
    for f in files:
        l_names.append(f["key"])
        link = "https://zenodo.org/record/{}/files/{}".format(record_id, l_names[-1]).replace(
            " ", "%20"
        )
        link_markdown = "[" + link + "](" + link + ")"
        l_links.append(link_markdown)
        l_size.append(f["size"] / 1024**2)
        # size = "{:.2f}".format(f["size"] / 1024**2) + " MB"

    data = OrderedDict(
        [
            ("Name", l_names),
            ("Size (MB)", l_size),
            ("Link", l_links),
        ]
    )
    df = pd.DataFrame(data)
    # df["id"] = df.index

    table = dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[
            {"id": x, "name": x, "presentation": "markdown"}
            if x == "Link"
            else {"id": x, "name": x}
            for x in df.columns
        ],
        sort_action="native",
        style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
        style_data={
            "backgroundColor": "rgb(50, 50, 50)",
            "color": "white",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_cell={"overflow": "hidden", "textOverflow": "ellipsis", "maxWidth": 0},
    )

    return table


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


def create_table_csv(url, n_rows=10, max_cols=20):
    rows = []
    header = []
    with closing(requests.get(url, stream=True)) as r:
        f = (line.decode("utf-8") for line in r.iter_lines())
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for idx, l_row in enumerate(reader):
            if idx == 0:
                header = [html.Tr([html.Th(col) for col in l_row[:max_cols]])]
            else:
                rows += [html.Tr([html.Td(cell) for cell in l_row[:max_cols]])]
            if idx > n_rows:
                break

    table = [html.Thead(header), html.Tbody(rows)]
    return dmc.Table(striped=True, highlightOnHover=True, children=table)

def create_geojson_preview(url):
    with closing(requests.get(url, stream=True)) as r:
        print(r)
        preview = dl.Map(dl.TileLayer(), style={'width': '1000px', 'height': '500px'})

        #dl.GeoJSON(url=r, id="capitals")
    return preview

def warning_non_suported_file(url):
    if url.strip('.')[-1] not in ['.json', '.csv', '.geojson']:
        return dbc.Alert("File not suported. Try another one.", color="primary"),

    