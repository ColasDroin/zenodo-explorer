from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Amazing Zenodo Dataset Explorer"
server = app.server

n_circles = 10


app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=[
        dmc.Affix(
            html.A(
                dmc.ThemeIcon(
                    DashIconify(
                        icon="radix-icons:github-logo",
                        width=22,
                    ),
                    radius=30,
                    size=36,
                    variant="outline",
                    color="gray",
                ),
                href="https://github.com/h4ck1ng-science/zenodo-explorer",
                target="_blank",
            ),
            position={"top": 20, "right": 20},
        ),
        html.Div(
            [
                html.Div(
                    className="area",
                    children=[
                        html.Ul(
                            className="circles", children=[html.Li() for i in range(n_circles)]
                        ),
                    ],
                    style={"z-index": "-1"},
                ),
                dcc.Store(id="dataset-url-store", data=""),
                dash.page_container,
            ]
        ),
        dmc.Center(
            dmc.Text(
                "Made with ❤️ by Carlos, Colas and Diogo for the CERN webfest 2022!",
                style={"color": "white"},
            ),
            style={"position": "absolute", "bottom": 20, "width": "100%"},
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
