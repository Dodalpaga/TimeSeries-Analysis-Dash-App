import dash
import glob
from dash_labs.plugins.pages import register_page
# Code from: https://github.com/plotly/dash-labs/tree/main/docs/demos/multi_page_example1
register_page(__name__, path="/ts")

import pandas as pd

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go # or plotly.express as px


fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)

sensors = ["Date","A","B","C","D","E","F","G"]
trials = glob.glob1("./uploads","*.csv")
list.sort(trials)

layout = html.Div([
    dcc.Dropdown(
        id="trial",
        options=[{"label": x[:-4], "value": x} for x in trials],
        value=trials[0],
        clearable=False,
        style={"width": "50%; color:#111111"}
    ),
    dcc.Dropdown(
        id="sensor",
        options=[{"label": x, "value": x} for x in sensors],
        value=sensors[0],
        clearable=False,
        style={"width": "50%; color:#111111"}
    ),
    dcc.Graph(figure=fig,id="ts-chart"),
])


@callback(Output("ts-chart", "figure"),[Input("sensor", "value") , Input("trial", "value")])
def update_bar_chart(sensor,dataset):
    df = pd.read_csv("./uploads/{}".format(dataset))
    print(df.shape)
    fig = go.Figure([go.Scatter(x=df['Date'], y=df[sensor])])
    return fig


