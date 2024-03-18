import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Create Dash app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

# Mapbox access token (replace with your own)
mapbox_access_token = "pk.eyJ1IjoiYWJyaWxoaWQiLCJhIjoiY2xoY3J5dnlpMHU0ajNtbXR1MW80cHd0aiJ9.4D2V1tHsx7FS8HFveyaz1Q"
mapbox_style = "mapbox://styles/mapbox/outdoors-v12"
# Dataset URL
my_dataset = "https://raw.githubusercontent.com/hidabril/ISOTOPOS_BOGOTA_SUB/main/Base_PGW_FULL.csv"

# Read data
df = pd.read_csv(my_dataset)
dff = df.copy()

# Site locations
site_lat = dff.Lat
site_lon = dff.Lon
site_PGW = dff["P/GW"]
site_tipo = dff.TIPO
cmax = df["P/GW"].sort_values(ascending=False).iloc[1]
cmin = df["P/GW"].sort_values(ascending=False).iloc[-1]
print(cmin)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

lineaY = [-28, -32.01, -36.02, -40.03, -44.04, -48.05, -52.06, -56.07, -60.08, -64.09, -68.1, -72.11, -76.12, -80.13, -84.14, -88.15, -92.16, -96.17, -100.18, -104.19, -108.2, -148.3]
lineaX = [-5, -5.5, -6, -6.5, -7, -7.5, -8, -8.5, -9, -9.5, -10, -10.5, -11, -11.5, -12, -12.5, -13, -13.5, -14, -14.5, -15, -20]

# Function to create filtered scatter plot figure based on selected points
def get_figure(selected_points):
    if selected_points and selected_points["points"]:
        filtered_df = dff.iloc[
            [
                p["pointNumber"]
                for p in selected_points["points"]
                if "pointNumber" in p
            ]
        ]
    else:
        filtered_df = dff.copy()
        
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_df["OXIG_18"],
            y=filtered_df["DEUT_2H"],
            mode="markers",
            name="Composición isotópica del agua subterránea"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=[-9.394303],
            y=[-65.224002],
            mode="markers",
            name="Composición isotópica de la precipitación anual",
            marker=dict(size=12,
                        symbol="diamond",
        
                        )
        )
    )
    
    fig.update_layout(
        template="plotly_white",
        title="Relación P/GW-δ18O precipitación y agua subterránea",
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0
        )
    )
    fig.add_trace(
        go.Scatter(
        x=lineaX,
        y=lineaY,
        name="Linea Meteórica Global (GMWL)",
        )

    )
    
    fig.update_xaxes(title_text='δ¹⁸O')
    fig.update_yaxes(title_text='δ²H')
    fig.update_xaxes(range=[-7, -13])
    fig.update_yaxes(range=[-30, -90])
    
    fig.show()
    return fig



# App layout
app.layout = html.Div(children=[
        html.Div([
        dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src="assets/logos.png", height="100px")),
                                dbc.Col(
                                    dbc.NavbarBrand("Isotopos Bogotá - Relación P/GW δ¹⁸O", className="ml-2"),
                                    #href="https://github.com/hidabril/ISOTOPOS_BOGOTA",  # Direct link
                                    #target="_blank",  # Open in new tab
                                ),
                                dbc.Col(
                                    [
                                        # GitHub icon using FontAwesome
                                        dbc.Button(
                                            "Ver código en Github",
                                            outline=True,
                                            color="primary",
                                            href="https://github.com/hidabril/ISOTOPOS_BOGOTA_SUB",
                                            id="gh-link",
                                            style={"text-transform": "none"},
                                        ),
                                    ],
                                    width="auto",  # Adjust width for alignment
                                )
                            ],
                            align="center",
                        ),
                        style={'text-decoration': 'none'}  # Remove underline from link
                    ),
                ]
            ),
        ),
    ]),
        
        html.Div(children=[
            dcc.Graph(
                id="sampling-points-map",
                style={"height": "90vh",'display': 'inline-block'},
                figure=go.Figure(
                    go.Scattermapbox(
                        lat=site_lat,
                        lon=site_lon,
                        mode="markers",
                        marker = dict(
                               size = 8,
                               symbol = 'circle',
                               colorscale = 'viridis',
                               color = site_PGW,
                               colorbar_title="P/GW",
                               colorbar_orientation="h",
                               cmax=cmax,
                               cmin=cmin,
                           ),
                    )
                ).update_layout(
                    autosize=True,
                    hovermode="closest",
                    title="Puntos de muestreos de agua subterránea",
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(lat=4.91, lon=-73.96),
                        pitch=0,
                        zoom=8.5,
                        style=mapbox_style,
                    ),
                ),
               ), 
             ], style={'display': 'inline-block'}),
        html.Div(children=[
            dcc.Graph(
                id="isotopic-composition",
                style={"height": "90vh",'display': 'inline-block'},
                figure=get_figure(None),
            ),
        ], style={'display': 'inline-block','width':'40%'}),
], style={'width': '100%', 'display': 'inline-block'})

# Callback to update scatter plot based on selected points in the map
@app.callback(
    Output("isotopic-composition", "figure"),
    Input("sampling-points-map", "selectedData"),
)
def update_isotopic_composition(selected_points):
    return get_figure(selected_points)

# Run the app
if __name__ == "__main__":
    app.run_server()
