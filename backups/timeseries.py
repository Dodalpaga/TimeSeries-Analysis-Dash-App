import dash
from dash import dcc, html, Input, Output, ctx, callback
import plotly.graph_objects as go # or plotly.express as px
import glob,os
from dash_labs.plugins.pages import register_page
import dash_bootstrap_components as dbc

import pandas as pd

# Code from: https://github.com/plotly/dash-labs/tree/main/docs/demos/multi_page_example1
register_page(__name__, path="/ts")

colors = {
    'background': '#dddddd',
    'grid': '#666666',
    'text': '#333333'
}

labels_list = ["Label 1", "Label 2", "Label 3"]

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
        html.Div(
            [dbc.Button("Regenerate Labels", color="danger", id="regenerate-button", className="me-1", n_clicks=0),
            html.Div("",style={'margin-left': '2.5%','margin-right': '2.5%'}),
            html.Div([dbc.Button(label, color="primary", id=label, className="me-1", n_clicks=0) for label in labels_list]),
            html.Div("",style={'margin-left': '2.5%','margin-right': '2.5%'})],
            style={'display':'flex', 'margin': '20px', 'align-items':'center', 'justify-content':'center'}
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



list_inputs = [Input("date_feature", "value"), Input("sensor", "value") , Input("dataset", "value"), Input("ts-chart", "figure"), Input("regenerate-button", "n_clicks")]
variable_inputs = [Input(label,"n_clicks") for label in labels_list]

from plotly.subplots import make_subplots
@callback(Output("ts-chart", "figure"), list_inputs + variable_inputs)
def update_chart(date_feature,sensor,dataset,figure, *args):
    # create an empty figure  with no data
    fig = go.Figure()
    fig.add_annotation(text="Choose a dataset, the time feature (column), and then the signal you want to display",showarrow=False,font=dict(size=20))
    if dataset != None:
        df = pd.read_csv("./uploads/{}".format(dataset))
        if date_feature!=None :
            # Si jamais le fichier csv "label" n'existe pas on le crée (vide == tout à 0)
            if not os.path.exists("./results/{}_labels.csv".format(dataset[:-4])) :
                df_labels = pd.DataFrame(df[date_feature])
                df_labels[labels_list] = 0
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            df_labels = pd.read_csv("./results/{}_labels.csv".format(dataset[:-4]))
            if "regenerate-button" == ctx.triggered_id:
                df_labels[labels_list] = 0
                df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
            for label in labels_list:
                if label == ctx.triggered_id:
                    print(label)
                    figure_data = figure["layout"]
                    range_of_slider = figure_data["xaxis"]["range"]
                    boundary_low =  df_labels.iloc[(df_labels['ts']-range_of_slider[0]).abs().argsort()[0]]["ts"]
                    boundary_high = df_labels.iloc[(df_labels['ts']-range_of_slider[1]).abs().argsort()[0]]["ts"]
                    df_labels.loc[df_labels["ts"].between(boundary_low,boundary_high),label]=1
                    df_labels.to_csv("./results/{}_labels.csv".format(dataset[:-4]),index=False)
                
            if sensor!=None :
                fig = make_subplots(rows = 2, cols = 1, 
                                    vertical_spacing=0.2,
                                    shared_xaxes=True,
                                    row_heights=[0.5,0.25],
                                    )
                fig.add_trace(go.Scatter(x=df[date_feature], y=df[sensor], name=sensor, legendgroup=1), row=1, col=1)
                for fault in labels_list:
                    fig.add_trace(go.Scatter(x=df_labels[date_feature], y=df_labels[fault], name=fault, legendgroup=2), row=2, col=1)
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
                fig.update_yaxes(row=2,col=1,range=[-0.1,1.1])
    return fig