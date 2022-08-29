import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc
import dash_leaflet as dl
import requests
import json
from contextlib import closing

import tools as tools
import dash_cytoscape as cyto
import numpy as np

from urllib.request import urlopen


# Cytoscape styling and layout
cyto.load_extra_layouts()
default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "width": "mapData(size, 0, 4, 20, 60)",
            "height": "mapData(size, 0, 4, 20, 60)",
            "content": "data(label)",
            "font-size": "11px",
            "text-valign": "center",
            "text-halign": "center",
            "color": "white",
        },
    }
]


dash.register_page(__name__, title="Amazing Zenodo Dataset Explorer")

layout = (
    html.Div(
        children=[
            dmc.Paper(
                dmc.Center(
                    html.A(
                        id="header-dataset-url",
                        children="No dataset selected",
                        href="#",
                        target="_blank",
                    )
                ),
                p=20,
                style={
                    "height": "5vh",
                    "width": "100vw",
                    "z-index": "1000",
                    "opacity": "0.7",
                    "border-radius": "0",
                },
            ),
            dmc.Center(
                html.Div(
                    children=[
                        dmc.Tabs(
                            position="center",
                            grow=False,
                            children=[
                                dmc.Tab(
                                    label="Graph exploration",
                                    children=[
                                        dmc.Center(
                                            html.Div(
                                                id="div-network",
                                                style={
                                                    "height": "80vh",
                                                    "width": "80vw",
                                                    "z-index": "1010",
                                                },
                                                className="border border-info rounded",
                                                children=cyto.Cytoscape(
                                                    id="cytoscape-graph",
                                                    style={"width": "100%", "height": "100%"},
                                                    layout={"name": "cola", "infinite": "true"},
                                                    stylesheet=default_stylesheet,
                                                ),
                                            ),
                                        ),
                                    ],
                                ),
                                dmc.Tab(
                                    label="Dataset description",
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dcc.Markdown(
                                                    id="description-output",
                                                    children="No dataset selected",
                                                )
                                            ],
                                            shadow="lg",
                                            withBorder=True,
                                            p=12,
                                        ),
                                    ],
                                ),
                                dmc.Tab(
                                    label="Dataset overview",
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                html.Div(
                                                    id="overview-output",
                                                    # color="dimmed",
                                                    children="No dataset selected",
                                                ),
                                            ],
                                            shadow="lg",
                                            withBorder=True,
                                            p=12,
                                        ),
                                    ],
                                ),
                                dmc.Tab(
                                    label="List of files",
                                    children=[
                                        html.Div(
                                            id="table-files-output",
                                            children="No dataset selected",
                                            className="w-100 h-100",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        # dmc.Group(
                        #     direction="row",
                        #     align="flex-start",
                        #     class_name="mt-2",
                        #     grow=False,
                        #     children=[
                        #         dmc.Group(
                        #             direction="column",
                        #             style={"width": "45vw"},
                        #             align="stretch",
                        #             children=[],
                        #         ),
                        #         dmc.Group(
                        #             direction="column",
                        #             style={"width": "45vw", "height": "80vh", "overflow": "auto"},
                        #             align="stretch",
                        #             children=[
                        #                 html.Div(
                        #                     id="div-table",
                        #                     className="w-100",
                        #                 ),
                        #             ],
                        #         ),
                        #     ],
                        # ),
                        dmc.Drawer(
                            title="Sample data for file X",
                            id="drawer-table",
                            padding="md",
                            size="60%",
                            zIndex=1020,
                            children=html.Div(
                                id="div-table",
                                className="w-100",
                            ),
                        ),
                        dcc.Link(
                            children=dmc.Button(
                                "Back to main page", variant="outline", color="yellow"
                            ),
                            href="/",
                            style={"position": "absolute", "bottom": "5rem", "right": "5rem"},
                        ),
                    ],
                    style={
                        "width": "95vw",
                        "height": "95vh",
                        "z-index": "1000",
                    },
                ),
            ),
        ],
    ),
)


@callback(
    Output(component_id="overview-output", component_property="children"),
    Output(component_id="description-output", component_property="children"),
    Output(component_id="cytoscape-graph", component_property="elements"),
    Output(component_id="header-dataset-url", component_property="children"),
    Output(component_id="table-files-output", component_property="children"),
    Input(component_id="dataset-url-store", component_property="data"),
    prevent_initial_call=True,
)
def update_dataset_URL(url_zenodo):
    if url_zenodo is not None and url_zenodo != "":
        # Get dataset json data from zenodo
        json_data = tools.return_dataset_json(url_zenodo)

        # Get corresponding metadata
        dic_metadata = tools.return_dataset_info(json_data)
        div_info_data = html.Div(
            children=[
                html.P(dic_metadata["Title"]),
                html.P(dic_metadata["Keywords"]),
                html.P(dic_metadata["Publication date"]),
                html.P(dic_metadata["DOI"]),
                html.P(dic_metadata["Total size"]),
            ]
        )
        dataset_description = tools.return_dataset_description(json_data)
        table_files = tools.return_table_files(json_data, url_zenodo)
        # Get files and build graph
        l_names, l_links, l_sizes = tools.return_dataset_files(json_data, url_zenodo)
        title_dataset = dic_metadata["Title"].split("Title: ")[1]

        ### Build graph
        # Declare central node, i.e. current dataset
        elements = [{"data": {"id": title_dataset, "label": title_dataset, "url": url_zenodo}}]
        # Declare nodes
        elements += [
            {"data": {"id": name, "label": name, "url": url, "size": size}}
            for name, url, size in zip(l_names, l_links, l_sizes)
        ]
        # Declare edges
        elements += [{"data": {"source": title_dataset, "target": name}} for name in l_names]

        return div_info_data, dataset_description, elements, dic_metadata["Title"], table_files
    return dash.no_update


@callback(
    Output(component_id="drawer-table", component_property="opened"),
    Output(component_id="div-table", component_property="children"),
    Output(component_id="drawer-table", component_property="title"),
    Input(component_id="cytoscape-graph", component_property="tapNodeData"),
    prevent_initial_call=True,
)
def update_table_click(data):
    if data is not None:
        if "url" in data and "label" in data:
            url = data["url"]
            label = data["label"]
            if url.endswith(".csv"):
                return True, tools.create_table_csv(url, n_rows=20), "Sample data for file " + label
            elif url.endswith(".geojson"):
                #url = 'https://raw.githubusercontent.com/shawnbot/topogram/master/data/us-states.geojson'

                response = urlopen(url)
                data_json = json.loads(response.read())
                data_json["features"] =  data_json["features"][:30]

                # data_json_basic = []
                # for f in data_json["features"]:
                #     for c in f["geometry"]["coordinates"][0][0]:
                #         if type(c) is not float:
                #             data_json_basic.append({"lat": c[0], "lon": c[1]})

                #{"lat":c[0], "lon": c[1]} for c in f["geometry"]["coordinates"]
                #print(data_json)

                #return True, dl.Map(dl.GeoJSON(data=data_json, id="geojson"), style={'width': '1000px', 'height': '500px'}), url
                return True, dl.Map(children=[dl.TileLayer()] + [dl.GeoJSON(data=data_json, id="geojson")], style={'width': '1000px', 'height': '500px'}), url

            
            else:
                return True, "File format not supported yet", url

    return dash.no_update


@callback(
    Output(component_id="header-dataset-url", component_property="href"),
    Input(component_id="dataset-url-store", component_property="data"),
    prevent_initial_call=False,
)
def update_url_header(url_zenodo):
    if url_zenodo is not None and url_zenodo != "":
        return url_zenodo
    return dash.no_update
