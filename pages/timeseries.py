import dash
import glob,os
from dash_labs.plugins.pages import register_page
import dash_bootstrap_components as dbc
# Code from: https://github.com/plotly/dash-labs/tree/main/docs/demos/multi_page_example1
register_page(__name__, path="/ts")

colors = {
    'background': '#333333',
    'text': '#ffffff'
}

faults = ["Printing","Warping","Layer_Shifting","Blobs_Layer_Separation","Not_Sticking_To_Bed","Stringing","Gaps","Colapsing","Not_Extruding"]

import pandas as pd

from dash import Dash, dcc, html, Input, Output, callback_context, callback
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
            style={'display':'flex', 'margin-top': '10px', 'align-items':'center'}
        ),
        html.Div(
            [html.Div("Choose the time feature", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="date_feature",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin-top': '10px', 'align-items':'center'}
        ),
        html.Div(
            [html.Div("Choose an other feature", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="sensor",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin-top': '10px', 'align-items':'center'}
        ),
        html.Div(
            dcc.Graph(
                figure=fig,
                id="ts-chart",
            ),
            style={'margin': '10px', 'justify-content':'center', 'align-items':'center'},
        ),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
        html.Div(
            [dbc.Button("Regenerate Labels", color="danger", id="generate-button", className="me-1", n_clicks=0),
            html.Div("",style={'margin-left': '2.5%','margin-right': '2.5%'}),
            dbc.Button("Warping", color="primary", id="warping-button", className="me-1", n_clicks=0),
            dbc.Button("Layer-Shifting", color="primary", id="layer-shifting-button", className="me-1", n_clicks=0),
            dbc.Button("Blobs / Layer-Separation", color="primary", id="blobs-button", className="me-1", n_clicks=0),
            dbc.Button("Not Sticking To Bed", color="primary", id="nstb-button", className="me-1", n_clicks=0),
            dbc.Button("Stringing", color="primary", id="stringing-button", className="me-1", n_clicks=0),
            dbc.Button("Gaps", color="primary", id="gaps-button", className="me-1", n_clicks=0),
            dbc.Button("Colapsing", color="primary", id="colapsing-button", className="me-1", n_clicks=0),
            dbc.Button("Not Extruding", color="primary", id="not-extruding--button", className="me-1", n_clicks=0),
            html.Div("",style={'margin-left': '2.5%','margin-right': '2.5%'}),
            dbc.Button("Impression en cours", color="success", id="printing-button", className="me-1", n_clicks=0)],
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
@callback(Output("ts-chart", "figure"),[Input("date_feature", "value"), Input("sensor", "value") , Input("dataset", "value"), Input("ts-chart", "figure"), Input("generate-button", "n_clicks"), Input("warping-button", "n_clicks"), Input("layer-shifting-button", "n_clicks"), Input("blobs-button", "n_clicks"), Input("nstb-button", "n_clicks"), Input("stringing-button", "n_clicks"), Input("gaps-button", "n_clicks"), Input("colapsing-button", "n_clicks"), Input("not-extruding--button", "n_clicks"), Input("printing-button", "n_clicks")])
def update_chart(date_feature,sensor,dataset,figure,n_generate,n_warping,n_layer_shifting,n_blobs,n_nstb,n_stringing,n_gaps,n_colapsing,n_not_extruding,n_printing):
    # create an empty figure  with no data
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                autorange=True,
            )
        )
    )
    fig.update_xaxes(showline=False, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=False, linewidth=2, linecolor='black')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#ffffff')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#ffffff')
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if dataset != None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        if date_feature!=None :
            # Si jamais le fichier csv "label" n'existe pas on le crée (vide == tout à 0)
            if not os.path.exists("./results/{}_labels.csv".format(dataset[:-4])) :
                df_labels = pd.DataFrame(df[date_feature])
                df_labels[faults] = 0
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            df_labels = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
            if "generate-button" in changed_id:
                df_labels[faults] = 0
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "warping-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Warping"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "layer-shifting-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Layer_Shifting"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "blobs-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Blobs_Layer_Separation"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "nstb-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Not_Sticking_To_Bed"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "stringing-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Stringing"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "gaps-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Gaps"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "colapsing-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Colapsing"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "not-extruding-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Not_Extruding"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if "printing-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Printing"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                
            if sensor!=None :
                fig = make_subplots(4, 1, 
                                    vertical_spacing=0.2, 
                                    shared_xaxes=True, 
                                    specs=[[{'rowspan': 2, 'colspan': 1}],[None],[{'rowspan': 1, 'colspan': 1}],[{'rowspan': 1, 'colspan': 1}]])
                fig.add_trace(go.Scatter(x=df[date_feature], y=df[sensor], name=sensor), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_labels[date_feature], y=df_labels["Printing"], name="Printing"), row=4, col=1)
                for fault in faults[1:]:
                    fig.add_trace(go.Scatter(x=df_labels[date_feature], y=df_labels[fault], name=fault), row=3, col=1)
                fig.update_layout(
                    plot_bgcolor=colors['background'],
                    paper_bgcolor=colors['background'],
                    font_color=colors['text'],
                    height=650,
                    xaxis=dict(
                        rangeslider=dict(
                            visible=True,
                            autorange=True,
                        )
                    )
                )
                fig.update_xaxes(showline=False, linewidth=2, linecolor='black')
                fig.update_yaxes(showline=False, linewidth=2, linecolor='black')
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#ffffff')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#ffffff')
    return fig