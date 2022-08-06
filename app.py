from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Amazing Zenodo Dataset Explorer"
server = app.server

n_circles = 10


app.layout = dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=[
        html.Div(
            [
                html.Div(
                    className="area",
                    children=[
                        html.Ul(
                            className="circles", children=[html.Li() for i in range(n_circles)]
                        ),
                    ],
                ),
                dcc.Store(id="dataset-url-store", data=""),
                # html.Div(
                #     [
                #         html.Div(
                #             dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
                #         )
                #         for page in dash.page_registry.values()
                #     ]
                # ),
                dash.page_container,
            ]
        )
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
