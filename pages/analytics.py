import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc
import tools as tools
import dash_cytoscape as cyto
import numpy as np

# Cytoscape styling and layout
cyto.load_extra_layouts()
default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "width": "mapData(size, 0, 4, 20, 60)",
            "height": "mapData(size, 0, 4, 20, 60)",
            "content": "data(label)",
            "font-size": "12px",
            "text-valign": "center",
            "text-halign": "center",
        },
    }
]


dash.register_page(__name__, title="Amazing Zenodo Dataset Explorer")

layout = html.Div(
    children=[
        dmc.Group(
            direction="row",
            align="flex-start",
            class_name="mt-2",
            grow=False,
            children=[
                dmc.Group(
                    direction="column",
                    style={"width": "48vw"},
                    align="stretch",
                    children=[
                        dmc.Paper(
                            children=[
                                dmc.Text(
                                    id="text-output", color="dimmed", children="No dataset selected"
                                ),
                            ],
                            shadow="lg",
                            withBorder=True,
                            p=12,
                            pl=15,
                            pr=15,
                            pb=10,
                            # class_name="w-100",  # mx-auto",
                            style={"height": "30vh", "overflow": "scroll"},
                        ),
                        html.Div(
                            id="div-network",
                            style={"height": "60vh", "overflow": "scroll"},
                            className="border border-info rounded",
                            children=cyto.Cytoscape(
                                id="cytoscape-graph",
                                layout={"name": "spread"},
                                stylesheet=default_stylesheet,
                            ),
                        ),
                    ],
                ),
                dmc.Group(
                    direction="column",
                    style={"width": "48vw", "height": "80vh", "overflow": "auto"},
                    align="stretch",
                    children=[
                        html.Div(
                            id="div-table",
                            className="w-100",
                        ),
                    ],
                ),
            ],
        ),
        dcc.Link(
            children=dmc.Button("Back to main page", variant="outline", color="orange"),
            href="/",
            style={"position": "absolute", "bottom": "5rem", "right": "5rem"},
        ),
    ],
    style={
        "width": "100%",
        "height": "100%",
        "position": "absolute",
        "overflow": "scroll",
        "margin-left": "1rem",
        "margin-right": "1rem",
    },
)


@callback(
    Output(component_id="text-output", component_property="children"),
    Output(component_id="cytoscape-graph", component_property="elements"),
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

        return div_info_data, elements
    return dash.no_update


@callback(
    Output(component_id="div-table", component_property="children"),
    Input(component_id="cytoscape-graph", component_property="tapNodeData"),
    prevent_initial_call=True,
)
def update_table_click(data):
    if data is not None:
        if "url" in data:
            url = data["url"]
            if url.endswith(".csv"):
                return tools.create_table_csv(url, n_rows=20)

    return dash.no_update
