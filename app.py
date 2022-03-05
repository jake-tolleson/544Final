import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import datetime
from PIL import Image


def draw_graph(id,*args, **kwargs):
    return html.Div([
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
GAMES.loc[679,'duration'] = '3:07'
GAMES.loc[579,'duration'] = '3:14'
GAMES.loc[624,'duration'] = '3:05'
GAMES.loc[773,'duration'] = '2:11'
GAMES.loc[312,'duration'] = '0:00'
GAMES.loc[483,'duration'] = '3:25'
GAMES.loc[491,'duration'] = '0:00'
GAMES.loc[781,'duration'] = '3:00'

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

#Weather: Categorizing
MERGED.loc[MERGED['weather'].str.contains('Sunny|Clear|fair|beautiful|nice', case = False)==True,'weather'] = 'Clear'
MERGED.loc[MERGED['weather'].str.contains('Cloudy|cldy|clouds|foggy|overcast|Haze', case = False)==True,'weather'] = 'Cloudy'
MERGED.loc[MERGED['weather'].str.contains('Rain|Showers|storms|scattered', case = False)==True,'weather'] = 'Rain'
MERGED.loc[MERGED['weather'].str.contains('Roof Closed|indoors|indoor|dome', case = False)==True,'weather'] = 'Indoors'
MERGED.loc[MERGED['weather'].str.contains('Humidity|Humid|Hot|Warm|Muggy', case = False)==True,'weather'] = 'Hot'
MERGED.loc[MERGED['weather'].str.contains('Cool', case = False)==True,'weather'] = 'Cold'
MERGED['weather'] = MERGED['weather'].replace({np.nan:'Unknown'})
MERGED['weather'] = MERGED['weather'].replace({'':'Unknown'})

# Need to be able to make summary statistics by SEC team
# List of SEC teams
SEC_teams = ['Alabama','Arkansas','Auburn','Florida','Mississippi State','Kentucky','South Carolina',
             'Ole Miss','Georgia','Tennessee','Texas A&M','LSU','Vanderbilt','Missouri']

# One hot-encode SEC teams
# A column for every team
# 1 if that team was in the game (home or away) 0 otherwise
for i in SEC_teams:
    MERGED[i] = np.where(MERGED['Matchup_Full_TeamNames'].str.contains(i),1,0)

# get summary statistics for each team
d = []
for i in SEC_teams:
    df = MERGED.loc[MERGED[i]==1,:] 
    d.append({
        'Team':i,
        'AvgViews':df['VIEWERS'].mean(),
        'Avgattend':df['Percent_of_Capacity'].mean()
    })
# turn the list of dictionaries into a dataframe
df = pd.DataFrame(d)
# sort the data frame by team name
df.sort_values('Team',inplace=True)

viewership = px.bar(data_frame=df,x='Team',y='AvgViews')
viewership.add_hline(df['AvgViews'].mean(),
            line_dash='dot',
            annotation_text="Average: "+str("{:,}".format(np.int64(df['AvgViews'].mean()))), 
            annotation_position="top right",
            annotation_font_size=12,
            annotation_font_color="black")
viewership.update_layout(title={
            'text':"Average TV Views Per Game by School",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_color="black",
        xaxis_title="School",
        yaxis_title="Number of Views")
viewership.layout.template = 'plotly_white'


attendance = px.bar(data_frame=df,x='Team',y='Avgattend')
attendance.add_hline(df['Avgattend'].mean(),
            line_dash='dot',
            annotation_text="Average: "+str(np.round(df['Avgattend'].mean(),2)), 
            annotation_position="top right",
            annotation_font_size=12,
            annotation_font_color="black")
attendance.update_layout(title={
            'text':"Average Percent of Capacity Per Game by School",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_color="black",
        xaxis_title="School",
        yaxis_title="Percent of Capacity")
attendance.layout.template = 'plotly_white'

# initialize app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
              meta_tags=[
                  {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                  ]
              )

app.layout = html.Div([
    html.Img(src = Image.open('logos\SEC.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
    html.H1('"It Just Means More"', style={'width': '90%','display': 'inline-block'}),
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Div([
                                    html.H2('Best Branded Teams: ')
                                ], style={'textAlign': 'center'}),
                                # html.Div([
                                #     dcc.Dropdown(
                                #         id = "input"
                                #         ),
                                #     ], style={'textAlign': 'center'}) 
                                ])
                            ),])
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Img(src = Image.open('logos/UA.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                html.Div([
                                    html.H4('Avg Viewers: '), #id='placeholder2'),
                                    ], style={'textAlign': 'center'})
                                ])
                        ),])
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Img(src = Image.open('logos/UA.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                html.Div([
                                    html.H4('Avg Ratings: ' ), #id='placeholder3'),
                                    ], style={'textAlign': 'center'})
                                ])
                            ),
                        ]) 
                ], width=3),
                dbc.Col([
                    html.Div([
                        dbc.Card(
                            dbc.CardBody([
                                html.Img(src = Image.open('logos/UGA.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                html.Div([
                                    html.H4('Avg Stadium Capacity: '), #id='placeholder4'),
                                    ], style={'textAlign': 'center'})
                                ])
                            ),
                        ]) 
                ], width=3),
                
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_graph(id='viewership',figure=viewership) 
                ], width=6),
                dbc.Col([
                    draw_graph(id='attendance',figure=attendance)
                ], width=6),
            ], align='center'), 
            html.Br(),     
        ]), color = 'light'
    )
])



# @app.callback(
#     [Output('viewership','figure'),
#      Output('attendance','figure'),
#      Output('relationship','figure'),
#      Output('placeholder1','children'),
#      Output('placeholder2','children'),
#      Output('placeholder3','children'),
#      Output('placeholder4','children')],
#     Input('input','value')
# )
# def update_graph(value):
#     pass

if __name__ == '__main__':
    app.run_server(debug=True) 
    