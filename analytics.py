import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc
import tools as tools
import dash_cytoscape as cyto
import numpy as np

cyto.load_extra_layouts()

dash.register_page(__name__, title="Amazing Zenodo Dataset Explorer")

layout = html.Div(
    children=[
        dmc.Paper(
            children=[
                dmc.Text(id="text-output", color="dimmed", children="No dataset selected"),
            ],
            shadow="lg",
            withBorder=True,
            pt=15,
            pl=15,
            pr=15,
            pb=10,
            mt=50,
            class_name="w-50 mx-auto",
        ),
        html.Div(id="div-network"),
        dmc.Center(
            dcc.Link(
                children=dmc.Button("Back to main page", variant="outline", color="orange"),
                href="/",
            ),
            style={"position": "absolute", "bottom": "5rem", "width": "100%"},
        ),
    ],
    style={
        "width": "100%",
        "height": "100%",
        "position": "absolute",
    },
)


@callback(
    Output(component_id="text-output", component_property="children"),
    Output(component_id="div-network", component_property="children"),
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

        # Stylesheet to change node size depending on the weight of the file
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

        # Build graph
        graph = cyto.Cytoscape(
            id="cytoscape",
            layout={"name": "spread"},
            elements=elements,
            stylesheet=default_stylesheet,
            className="w-50 mx-auto mt-2 border border-info rounded",
        )

        return div_info_data, graph
    return dash.no_update
