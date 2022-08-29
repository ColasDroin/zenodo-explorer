import dash
from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import time
import random

dash.register_page(__name__, path="/", title="Amazing Zenodo Dataset Explorer")

layout = html.Div(
    children=dmc.Center(
        children=[
            dmc.Group(
                direction="row",
                align="flex-end",
                position="center",
                children=[
                    dmc.TextInput(
                        id="text-input",
                        label="Please enter a zenodo URL",
                        size="xl",
                        placeholder="https://zenodo.org/record/...",
                        style={"width": "50vw"},
                    ),
                    dcc.Link(
                        id="link-submit",
                        children=dmc.Button(
                            "Previsualize dataset",
                            id="load-dataset",
                            leftIcon=[DashIconify(icon="fluent:database-plug-connected-20-filled")],
                            size="xl",
                            color="blue",
                        ),
                        href="/analytics",
                    ),
                    dmc.Button(
                        "Generate example link",
                        id="generate-link",
                        leftIcon=[DashIconify(icon="carbon:task-star")],
                        size="xl",
                        color="blue",
                    ),
                ],
            ),
        ],
        class_name="w-100 h-100",
    ),
    style={
        "width": "100%",
        "height": "70%",
        "position": "absolute",
    },
)


@callback(
    Output(component_id="dataset-url-store", component_property="data"),
    State(component_id="text-input", component_property="value"),
    Input("load-dataset", "n_clicks"),
    prevent_initial_call=True,
)
def update_dataset_URL(input_value, n_clicks):
    if input_value is not None:
        # Delay to ensure the callback is returned after the new page has been loaded
        time.sleep(0.01)
        return input_value
    return dash.no_update


@callback(
    Output(component_id="load-dataset", component_property="disabled"),
    Output(component_id="link-submit", component_property="href"),
    Input(component_id="text-input", component_property="value"),
    prevent_initial_call=True,
)
def disable_button(input_value):
    if not input_value.startswith("https://zenodo.org/record/"):
        return True, "/"
    return False, "/analytics"


@callback(
    Output(component_id="text-input", component_property="value"),
    Input(component_id="generate-link", component_property="n_clicks"),
    prevent_initial_call=True,
)
def generate_link(n_clicks):
    if n_clicks is not None:
        return random.choice(
            [
                "https://zenodo.org/record/5887261",
                # "https://zenodo.org/record/3694065",
                # "https://zenodo.org/record/5796200",
                # "https://zenodo.org/record/3631254",
            ]
        )
    return dash.no_update
