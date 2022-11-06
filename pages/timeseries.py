import dash
from dash import dcc, html, Input, Output, ctx, callback, State, ALL
import plotly.graph_objects as go # or plotly.express as px
import glob,os
from dash_labs.plugins.pages import register_page
import dash_bootstrap_components as dbc
import os
import json
import ast

import pandas as pd

# Code from: https://github.com/plotly/dash-labs/tree/main/docs/demos/multi_page_example1
register_page(__name__, path="/ts")

colors = {
    'background': '#dddddd',
    'grid': '#666666',
    'text': '#333333'
}

fig = go.Figure() # or any Plotly Express function e.g. px.bar(...)
labels_list = []
df_labels = pd.DataFrame()

layout = html.Div(
    id='parent',
    children=[
        html.Div(
            [html.Div("Choose a Dataset", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="dataset",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin': '10px', 'align-items':'center'}
        ),
        html.Div(
            [html.Div("Choose the time feature", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="date_feature",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin': '10px', 'align-items':'center'}
        ),
        html.Div(
            [html.Div("Choose an other feature", style={'margin-right': '10px'}),
             dcc.Dropdown(
                 id="sensor",
                clearable=False,
                style={'width': '30%', 'color':'#111111'},
            )],
            style={'display':'flex', 'margin': '10px', 'align-items':'center'}
        ),
        html.Div(
            dcc.Graph(
                figure=fig,
                id="ts-chart",
            ),
            style={'margin': '10px', 'justify-content':'center', 'align-items':'center'},
        ),
        html.Div([
            html.Div([
                html.Div(
                    children=[
                        dbc.Button(
                            'Add Label', 
                            id='add-label', 
                            n_clicks=0,
                            className="me-1"
                            ),
                        dcc.Input(
                            id='input-label', 
                            type='text', 
                            value='Montreal'
                            ),
                        ]),
                dbc.Button("Regenerate Labels", color="danger", id="regenerate-button", className="me-1", n_clicks=0, style={"margin-top":"5px"})],
                style={'display':'flex', 'flex-direction':'column', 'margin': '10px', 'align-items':'center', 'justify-content':'center', 'width':'315px'}
                ),
            html.Div(id='container_labels', children=[], style={'display':'flex', 'flex-direction':'row', 'margin': '10px', 'align-items':'center'})
            ],style={'display':'flex'})
        ]
    )

@callback(output=Output('dataset', 'options'),
              inputs=[Input('parent', 'n_clicks')])
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
@callback(Output('container_labels', 'children'),
        State('input-label', 'value'),
        Input({'type': 'remove-label', 'index': ALL}, 'n_clicks'),
        State('container_labels', 'children'),
        Input('add-label', 'n_clicks'),
        Input("date_feature", "value"), 
        Input("sensor", "value") , 
        Input("dataset", "value"), 
        Input("regenerate-button", "n_clicks")
)
def update_labels(input_label, n, div_children, add_clicks,date_feature, sensor, dataset, regenerate):
    # create an empty figure  with no data
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    elm_in_div = len(div_children)
    div_children = []
    fig = go.Figure()
    labels_list=[]
    df_labels = pd.DataFrame()
    df= pd.DataFrame()
    fig.add_annotation(text="Choose a dataset, the time feature (column), and then the signal you want to display",showarrow=False,font=dict(size=20))
    if dataset != None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        if ctx.triggered_id == "regenerate-button":
            print("Removing dataset")
            os.remove("./results/{}_labels.csv".format(dataset[:-4]))
        else:
            if date_feature!=None :
                try :
                    df_labels = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
                    labels_list = list(df_labels.columns[1:])
                except :
                    print("Creating labels file")
                    df_labels = pd.DataFrame()
                    df_labels[date_feature] = df[date_feature]
                    print("Created labels file")
                    df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                    labels_list=[]
                    
                div_children = [html.Div(
                            id={'type':'Label', 'index':idx},
                            children=[
                                dbc.Button(
                                    label,
                                    id=label
                                    ),
                                dbc.Button(
                                    'X',
                                    id={'type': 'remove-label','index': idx}, 
                                    color="danger",
                                    style={"width":"50px", "padding":"0px"}
                                    )
                                ],
                            style={'flex-direction': 'column', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', "margin":"5px"}
                            ) for idx,label in enumerate(labels_list)]
                
                
                if 'remove-label' in triggered_id:
                    for idx, val in enumerate(n):
                        if val is not None:
                            df_labels = df_labels.drop(labels_list[idx],axis=1)
                            df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                            del labels_list[idx]
                            del div_children[idx]
                            print(f"All the remove buttons: {n}")
                            print(f"The index pertaining to the remove button clicked: {idx}")
                            print(f"The number of time this particualr remove button was clicked: {val}")
                            print(f"The new labels list: {labels_list}")

                elif 'add-label' in triggered_id and input_label.lower() not in [x.lower() for x in labels_list]:
                    labels_list.append(input_label)
                    df_labels[input_label]=0
                    df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                    print("Added label")
                    new_child = html.Div(
                        id={'type':'Label', 'index':elm_in_div},
                        children=[
                            dbc.Button(
                                input_label,
                                id=input_label
                                ),
                            dbc.Button(
                                'X',
                                id={'type': 'remove-label','index': elm_in_div}, 
                                color="danger",
                                style={"width":"50px", "padding":"0px"}
                                )
                            ],
                        style={'flex-direction': 'column', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center', "margin":"5px"}
                        )
                    div_children.append(new_child)
    return div_children

@callback(Output("ts-chart", "figure"),
        State('input-label', 'value'),
        Input({'type': 'remove-label', 'index': ALL}, 'n_clicks'),
        Input('container_labels', 'children'),
        Input('add-label', 'n_clicks'),
        Input("ts-chart", "figure"), 
        Input("date_feature", "value"), 
        Input("sensor", "value") , 
        Input("dataset", "value"),
        Input({'type':'Label', 'index': ALL}, 'n_clicks'),
        )
def update_fig(input_label, n, div_children, add_clicks,figure,date_feature, sensor, dataset, test_list):
    fig = go.Figure()
    fig.add_annotation(text="Choose a dataset, the time feature (column), and then the signal you want to display",showarrow=False,font=dict(size=20))
    if dataset != None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        if date_feature!=None :
            try :
                df_labels = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
                labels_list = list(df_labels.columns[1:])
            except :
                print("Creating labels file")
                df_labels = pd.DataFrame()
                df_labels[date_feature] = df[date_feature]
                print("Created labels file")
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                labels_list=[]
            if sensor!=None :
                if len(labels_list)>0:
                    if str(ctx.triggered_id)[0]=="{":
                        trigger = ast.literal_eval(str(ctx.triggered_id))
                        if trigger["type"]=="Label":
                            label = labels_list[trigger["index"]]
                            figure_data = figure["layout"]
                            range_of_slider = figure_data["xaxis"]["range"]
                            boundary_low =  df_labels.iloc[(df_labels[date_feature]-range_of_slider[0]).abs().argsort()[0]][date_feature]
                            boundary_high = df_labels.iloc[(df_labels[date_feature]-range_of_slider[1]).abs().argsort()[0]][date_feature]
                            df_labels.loc[df_labels[date_feature].between(boundary_low,boundary_high),label]=1
                            df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                    fig = make_subplots(rows = 2, cols = 1, 
                                        vertical_spacing=0.2,
                                        shared_xaxes=True,
                                        row_heights=[0.5,0.25],
                                        )
                    fig.add_trace(go.Scatter(x=df[date_feature], y=df[sensor], name=sensor, legendgroup=1), row=1, col=1)
                    for fault in labels_list:
                        fig.add_trace(go.Scatter(x=df_labels[date_feature], y=df_labels[fault], name=fault, legendgroup=2), row=2, col=1)
                    fig.update_yaxes(row=2,col=1,range=[-0.1,1.1])
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df[date_feature], y=df[sensor], name=sensor, legendgroup=1))
                fig.update_layout(
                    plot_bgcolor=colors['background'],
                    paper_bgcolor=colors['background'],
                    font_color=colors['text'],
                    height=550,
                    xaxis=dict(
                        rangeslider=dict(
                            visible=False,
                            autorange=True,
                        )
                    ),
                    # showlegend=False,
                    legend_tracegroupgap = 240,
                    hovermode='x unified'
                )
                fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
                fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
                fig.update_xaxes(showgrid=True, gridwidth=1.5, gridcolor=colors["grid"])
                fig.update_yaxes(showgrid=True, gridwidth=1.5, gridcolor=colors["grid"])
    return fig