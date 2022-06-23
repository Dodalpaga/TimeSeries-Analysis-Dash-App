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
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
        html.Div(
            [dbc.Button("Regenerate Labels", color="danger", id="generate-button", className="me-1", n_clicks=0),
             html.Div("",style={'margin-left': '5%','margin-right': '5%'}),
            dbc.Button("Warping", color="success", id="warping-button", className="me-1", n_clicks=0),
            dbc.Button("Update", color="warning", id="update-button", className="me-1", n_clicks=0)],
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
@callback(Output("ts-chart", "figure"),[Input("date_feature", "value"), Input("sensor", "value") , Input("dataset", "value"), Input("ts-chart", "figure"), Input("generate-button", "n_clicks"), Input("warping-button", "n_clicks")])
def update_chart(date_feature,sensor,dataset,figure,n_generate,n_warping):
    # create an empty figure  with no data
    fig = go.Figure()
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    print(changed_id)
    if dataset != None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        if date_feature!=None :
            # Si jamais le fichier csv "label" n'existe pas on le crée (vide == tout à 0)
            if not os.path.exists("./results/{}_labels.csv".format(dataset[:-4])) :
                df_labels = pd.DataFrame(df[date_feature])
                df_labels[defaults] = 0
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            df_labels = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
            if "generate-button" in changed_id:
                df_labels[defaults] = 0
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            # Si on clique sur le bouton "Warping", on récupère les labels générés par le slider tout en bas de la page
            if "warping-button" in changed_id :
                figure_data = figure["layout"]
                range_of_slider = figure_data["xaxis2"]["range"]
                boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),"Warping"]=1
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            if sensor!=None :
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
    return fig