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

layout = html.Div(
    id='dropdowns-parent',
    children=[
        dcc.Dropdown(
            id="dataset",
            # options=[{"label": x[:-4], "value": x} for x in datasets],
            clearable=False,
            style={"width": "50%; color:#111111"}
        ),
        dcc.Dropdown(
            id="date_feature",
            clearable=False,
            style={"width": "50%; color:#111111"}
        ),
        dcc.Dropdown(
            id="sensor",
            clearable=False,
            style={"width": "50%; color:#111111"}
        ),
        dcc.Graph(figure=fig,id="ts-chart"),
    ]
)

# @callback(Output("dataset","options"),Input("file-list","children"))
# def update_dataset_list(file_list):
#     print(file_list)
#     datasets = glob.glob1("./uploads","*.csv")
#     list.sort(datasets)
#     return("Oui")

@callback(output=dash.dependencies.Output('dataset', 'options'),
              inputs=[dash.dependencies.Input('dropdowns-parent', 'n_clicks')])
def change_my_dropdown_options(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    datasets = glob.glob1("./uploads","*.csv")
    list.sort(datasets)
    return(datasets)


@callback([Output("sensor", "options"),Output("date_feature", "options")],Input("dataset", "value"))
def update_sensor_dropdown(dataset):
    if dataset!=None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        return df.columns,df.columns
    else:
        return [],[]



@callback(Output("ts-chart", "figure"),[Input("date_feature", "value"), Input("sensor", "value") , Input("dataset", "value")])
def update_bar_chart(date_feature,sensor,dataset):
    if date_feature!=None and sensor!=None and dataset!=None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        fig = go.Figure([go.Scatter(x=df[date_feature], y=df[sensor])])
    else:
        # create an empty figure  with no data
        fig = go.Figure()
    return fig


