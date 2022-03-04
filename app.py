import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import datetime
from PIL import Image

def draw_graph(id,*args, **kwargs):
    html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    id=id,*args,**kwargs
                    )
                ])
            ),
        ])

# initialize app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
              meta_tags=[
                  {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                  ]
              )

app.layout = html.Div([
    html.Img(src = Image.open('SEC.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
    html.H1('"It Just Means More"', style={'width': '90%','display': 'inline-block'}),
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H2('Select a Team')
                                ], style={'textAlign': 'center'}),
                                html.Div([
                                    dcc.Dropdown(
                                        id = "input"
                                        ),
                                    ], style={'textAlign': 'center'}) 
                                ])
                            ),])
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H1(id='placeholder2'),
                                    ], style={'textAlign': 'center'})
                                ])
                        ),])
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H1(id='placeholder3'),
                                    ], style={'textAlign': 'center'})
                                ])
                            ),
                        ]) 
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H2(id='placeholder4'),
                                    ], style={'textAlign': 'center'})
                                ])
                            ),
                        ]) 
                ], width=3),
                
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_graph(id='viewership') 
                ], width=6),
                dbc.Col([
                    draw_graph(id='attendance')
                ], width=6),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_graph(id='relationship')
                ],width=12)
            ],align='center') ,
            html.Br(),     
        ]), color = 'light'
    )
])



@app.callback(
    [Output('viewership','figure'),
     Output('attendance','figure'),
     Output('relationship','figure'),
     Output('placeholder1','children'),
     Output('placeholder2','children'),
     Output('placeholder3','children'),
     Output('placeholder4','children')],
    Input('input','value')
)
def update_graph(value):
    pass


if __name__ == '__main__':
    app.run_server(debug=True) 
    