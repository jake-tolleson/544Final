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

# Read in files
# Need pandas version > 1.4 and pyarrow installed
RATINGS = pd.read_csv('TV_Ratings_onesheet.csv',engine='pyarrow')
GAMES = pd.read_csv('games_flat_xml_2012-2018.csv',engine='pyarrow')
CAPACITY = pd.read_csv('capacity.csv',engine='pyarrow')

# clean these duration formats
GAMES['duration'][679] = '3:07'
GAMES['duration'][579] = '3:14'
GAMES['duration'][624] = '3:05'
GAMES['duration'][773] = '2:11'
GAMES['duration'][312] = '0:00'
GAMES['duration'][483] = '3:25'
GAMES['duration'][491] = '0:00'
GAMES['duration'][781] = '3:00'

# function to convert duration into minutes
def duration_minutes(time):
    hour = np.int16(time.split(':')[0]) * 60
    minutes = np.int16(time.split(':')[1])
    return hour+minutes

# use function on duration column
GAMES['duration_minutes'] = GAMES['duration'].apply(duration_minutes)

# this attendance value is a typo
GAMES.loc[GAMES['attend'] > 200000,'attend'] = 71004

# merge the 3 datasets
MERGED = pd.merge(GAMES,RATINGS,how='inner',on='TeamIDsDate')
# capacity is a custom dataset
MERGED = pd.merge(MERGED,CAPACITY,on=['homename','stadium'])

# a KPI we will use is perecent of capacity
MERGED['Percent_of_Capacity'] = MERGED['attend']/MERGED['Capacity']

# compute total tds scored
MERGED['total_td'] = MERGED[['rush_td_home','pass_td_home','rush_td_vis','pass_td_vis']].sum(axis=1)
# compute total points scored
MERGED['total_pts'] = MERGED[['score_home','score_vis']].sum(axis=1)
# compute point differential
MERGED['pts_diff'] = np.abs(MERGED['score_home'] - MERGED['score_vis'])

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
    