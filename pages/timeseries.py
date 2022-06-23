from unicodedata import name
import dash
import glob,os
from dash_labs.plugins.pages import register_page
import dash_bootstrap_components as dbc
# Code from: https://github.com/plotly/dash-labs/tree/main/docs/demos/multi_page_example1
register_page(__name__, path="/ts")

colors = {
    'background': '#dedede',
    'text': '#292929'
}

defaults = ["Warping","Layer_Shifting","Blobs_Layer_Separation","Not_Sticking_To_Bed","Stringing","Gaps","Colapsing","Not_Extruding"]

import pandas as pd

from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go # or plotly.express as px


fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)

layout = html.Div(
    id='dropdowns-parent',
    children=[
        html.Div(
            [html.Div("Choose a Dataset", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="dataset",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin-top': '20px', 'align-items':'center'}
        ),
        html.Div(
            [html.Div("Choose the time feature", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="date_feature",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin-top': '20px', 'align-items':'center'}
        ),
        html.Div(
            [html.Div("Choose an other feature", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="sensor",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin-top': '20px', 'align-items':'center'}
        ),
        dcc.Graph(
            figure=fig,
            id="ts-chart",
            style={'display':'flex','margin': '20px','height': '100%','width': '100%'},
        ),
        html.Div(
            [dbc.Button("Regenerate Labels", color="danger", id="generate-button", className="me-1", n_clicks=0),
             html.Div("",style={'margin-left': '5%','margin-right': '5%'}),
            dbc.Button("Warping", color="success", id="warping-button", className="me-1", n_clicks=0),
            dbc.Button("Layer_Shifting", color="warning", id="ls-button", className="me-1", n_clicks=0),
            dbc.Button("Blobs_Layer_Separation", color="primary", id="blobs-ls-button", className="me-1", n_clicks=0),
            dbc.Button("Not_Sticking_To_Bed", color="info", id="nstb-button", className="me-1", n_clicks=0),
            dbc.Button("Gaps", color="light", id="gaps-button", className="me-1", n_clicks=0),
            dbc.Button("Colapsing", color="dark", id="colapse-button", className="me-1", n_clicks=0),
            dbc.Button("Not_Extruding", color="secondary", id="NotExtr-button", className="me-1", n_clicks=0),
            html.Span(id="generate-output", style={"verticalAlign": "middle","display":"flex"}),
            html.Span(id="warping-output", style={"verticalAlign": "middle","display":"flex"})],
            style={'display':'flex', 'margin-top': '20px', 'align-items':'center', 'justify-content':'center'}
        )
    ]
)

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

from plotly.subplots import make_subplots
@callback(Output("ts-chart", "figure"),[Input("date_feature", "value"), Input("sensor", "value") , Input("dataset", "value")])
def update_chart(date_feature,sensor,dataset):
    if dataset != None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        if date_feature!=None :
            if sensor!=None :
                # Si jamais le fichier csv "label" n'existe pas on le crée (vide == tout à 0)
                if not os.path.exists("./results/{}_labels.csv".format(dataset[:-4])) :
                    labels_df = pd.DataFrame(df[date_feature])
                    labels_df[defaults] = 0
                    labels_df.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                df_labels = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
                fig = make_subplots(2, 1, vertical_spacing=0.05, shared_xaxes=True)
                fig.add_trace(go.Scatter(x=df[date_feature], y=df[sensor], name=sensor), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_labels[date_feature], y=df_labels["Warping"], name="Warping"), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_labels[date_feature], y=df_labels["Layer_Shifting"], name="Layer_Shifting"), row=2, col=1)
                    
                fig.update_layout(
                    plot_bgcolor=colors['background'],
                    paper_bgcolor=colors['background'],
                    font_color=colors['text'],
                    width=1680,
                    height=600,
                    xaxis2=dict(
                        scaleanchor="x2",
                        rangeslider=dict(
                            visible=True,
                            autorange=True,
                        )
                    )
                )
            else:
                # create an empty figure  with no data
                fig = go.Figure()
        else:
            # create an empty figure  with no data
            fig = go.Figure()
    else:
        # create an empty figure  with no data
        fig = go.Figure()
            # if date_feature!=None and dataset!=None and sensor!=None and (n_generate>0 or n_warping>0):
            #     fig.update_layout()
    return fig

@callback(
    Output("generate-output", "children"), [Input("generate-button", "n_clicks"),Input("date_feature", "value") , Input("dataset", "value")]
)
def regenerate_labels(n_generate,date_feature,dataset):
    if n_generate > 0 and date_feature!=None and dataset!=None:
        labels_df = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
        labels_df[defaults] = 0
        labels_df.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
        return f"Clicked {n_generate} times."
    else:
        return "Not clicked."
    
@callback(
    Output("warping-output", "children"), [Input("warping-button", "n_clicks"),Input("date_feature", "value") , Input("dataset", "value"), Input("ts-chart", "figure")]
)
def testing_boundaries(n_warping,date_feature,dataset,fig):
    if n_warping > 0 and date_feature!=None and dataset!=None:
        figure_data = fig["layout"]
        range_of_slider = figure_data["xaxis2"]["range"]
        df = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
        boundary_low =  df.iloc[(df['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
        boundary_high = df.iloc[(df['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
        df.loc[df["ts"].between(boundary_low,boundary_high),"Warping"]=1
        df.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
        return f"Slider range {range_of_slider}."
    else:
        return "Not clicked."