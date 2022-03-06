import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import datetime
from PIL import Image
import layouts
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
#from layouts import Page1Layout, Page2Layout

# Function to create graphs
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


# Function to choose correct logo
def choose_logo(team):
    if team == 'Georgia':
        value = 'logos/UGA.png'
    elif team == 'Alabama':
        value = 'logos/UA.png'
    elif team == 'Missouri':
        value =  'logos/MU.png'
    elif team == 'Mississippi (Ole Miss)':
        value =  'logos/OM.png'
    elif team == 'Mississippi State':
        value = 'logos/MSU.png'
    elif team == 'Florida':
        value = 'logos/UF.png'
    elif team == 'Tennessee':
        value = 'logos/UT.png'
    elif team == 'LSU':
        value = 'logos/LSU.png'
    elif team == 'Texas A&M':
        value = 'logos/TAM.png'
    elif team == 'Kentucky':
        value = 'logos/UK.png'
    elif team == 'Auburn' :
        value =  'logos/AU.png'
    elif team == 'Vanderbilt':
        value = 'logos/VU.png'
    elif team == 'Arkansas':
        value = 'logos/UAK.png'
    elif team == 'South Carolina':
        value = 'logos/USC.png'
    else: value = 'logos/SEC.png'
    return value
    

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

# Engineer new variable: summed ranks of teams playing
import plotly.graph_objects as go
MERGED['rank_home'].unique()
MERGED['rank_home'] = MERGED['rank_home'].replace({'character(0)':'26'})
MERGED['rank_home'] = MERGED['rank_home'].astype(int)
MERGED['rank_vis'].unique()
MERGED['rank_vis'] = MERGED['rank_vis'].replace({'character(0)':'26'})
MERGED['rank_vis'] = MERGED['rank_vis'].astype(int)
MERGED['added_rank'] = MERGED['rank_home'] + MERGED['rank_vis']

# define lists of individual rankings and viewers
ranks = []
views=[]
ranks_vis=[]

ranks = [rank for rank in MERGED['rank_home']]
home = [team for team in MERGED['homename']]
ranks_vis = [rank for rank in MERGED['rank_vis']]
vis = [team for team in MERGED['visname']]
ranks.extend(ranks_vis)
views = [views for views in MERGED['VIEWERS']]
views.extend(views)
teams = home + vis

# Define figures with average stats per team
# avg viewers graph
viewership = px.bar(data_frame=df,x='Team',y='AvgViews')
viewership.add_hline(df['AvgViews'].mean(),
            line_dash='dot',
            annotation_text="Average: "+str("{:,}".format(np.int64(df['AvgViews'].mean()))), 
            annotation_position="top right",
            annotation_font_size=12,
            annotation_font_color="red")
viewership.update_layout(title={
            'text':"Average TV Views Per Game by School",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        title_font_color="black",
        xaxis_title="School",
        yaxis_title="Number of Views")
viewership.update_traces(marker_color='navy')
viewership.layout.template = 'plotly_white'

# avg attendance graph
attendance = px.bar(data_frame=df,x='Team',y='Avgattend')
attendance.add_hline(df['Avgattend'].mean(),
            line_dash='dot',
            annotation_text="Average: "+str(np.round(df['Avgattend'].mean(),2)), 
            annotation_position="top right",
            annotation_font_size=12,
            annotation_font_color="red")
attendance.update_traces(marker_color='navy')
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

# summed rank graph
summed_ranks_data=MERGED['added_rank']
summed_ranks = go.Figure(data=[go.Scatter(x=MERGED['added_rank'], y=MERGED['VIEWERS'], mode='markers',
                                 marker=dict(color='navy'),
                                 text=summed_ranks_data,
                                 hovertemplate = "<b>Summed Rank of Teams: </b> %{text} <br>")])

summed_ranks.update_xaxes(range=[0,51.5], title_text = 'Summed Rank of Teams per Game')
summed_ranks.update_yaxes(title_text = 'Viewers per Game')
summed_ranks.update_layout(title_text='Viewership by Matchup Weight')
summed_ranks.add_layout_image(
    dict(
        source= Image.open('logos/SEC.png'),
        xref="x",
        yref="y",
        x=0,
        y=16000000,
        sizex=45,
        sizey=16000000,
        sizing = 'stretch',
        opacity=0.1,
        layer="below")
    )
    # Set templates
summed_ranks.update_layout(template="plotly_white")

# Networks Graph
y0= MERGED[MERGED['Network']=='CBS']['added_rank']
y1 = MERGED[MERGED['Network']=='ESPN']['added_rank']
y3 = MERGED[MERGED['Network']=='ESPN2']['added_rank']
y4 = MERGED[MERGED['Network']=='ABC']['added_rank'] 

networks = go.Figure()
networks.add_trace(go.Box(y=y0, name='CBS', boxpoints='all'))
networks.add_trace(go.Box(y=y1, name='ESPN', boxpoints='all'))
networks.add_trace(go.Box(y=y3, name='ESPN2',boxpoints='all'))
networks.add_trace(go.Box(y=y4, name='ABC',boxpoints='all'))


networks.add_layout_image(
    dict(
        source= Image.open('logos/SEC.png'),
        xref="x",
        yref="y",
        x=0,
        y=50,
        sizex=3,
        sizey=50,
        sizing = 'stretch',
        opacity=0.1,
        layer="below")
    )
    # Set templates
networks.update_layout(template="plotly_white")
networks.update_xaxes( title_text = 'Network')
networks.update_yaxes(title_text = 'Summed Rank')
networks.update_layout(title_text='Weighted Matchup Distribution by Network')

# Figure for ranks of single teams
ranks_views = go.Figure(data=[go.Scatter(x=ranks, y=views, mode='markers',
                                 marker=dict(color='navy'),
                                 text=teams,
                                 hovertemplate = "<b>Team: </b> %{text} <br>"
                                 )])
ranks_views.add_layout_image(
    dict(
        source= Image.open('logos/SEC.png'),
        xref="x",
        yref="y",
        x=0,
        y=15000000,
        sizex=30,
        sizey=15000000,
        sizing = 'stretch',
        opacity=0.1,
        layer="below")
    )
    # Set templates
ranks_views.update_layout(template="plotly_white")
ranks_views.update_xaxes( title_text = 'Ranking')
ranks_views.update_yaxes(title_text = 'Views')
ranks_views.update_layout(title_text='Viewership by Ranking')



# Creating an object for "options" in the dropdown menu.
team_names_dict = [{'label': 'Georgia', 'value': 'Georgia'},
                   {'label': 'Alabama', 'value': 'Alabama'},
                   {'label': 'Missouri', 'value': 'Missouri'},
                   {'label': 'Mississippi (Ole Miss)', 'value': 'Mississippi (Ole Miss)'},
                   {'label': 'Mississippi State', 'value': 'Mississippi State'},
                   {'label': 'Florida', 'value': 'Florida'},
                   {'label': 'Tennessee', 'value': 'Tennessee'},
                   {'label': 'LSU', 'value': 'LSU'},
                   {'label': 'Texas A&M', 'value': 'Texas A&M'},
                   {'label': 'Kentucky', 'value': 'Kentucky'},
                   {'label': 'Auburn', 'value': 'Auburn'},
                   {'label': 'Vanderbilt', 'value': 'Vanderbilt'},
                   {'label': 'Arkansas', 'value': 'Arkansas'},
                   {'label': 'South Carolina', 'value': 'South Carolina'}]

# initialize app
app = Dash(suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP],
              meta_tags=[
                  {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                  ]
              )

# layout
app.layout = html.Div([

    # sec logo and slogan
    html.Img(src = Image.open('logos\SEC.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
    html.H1('"It Just Means More"', style={'width': '90%','display': 'inline-block'}),
    
    # create 3 tabs
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Best Branded Teams', value='tab-1'),
        dcc.Tab(label='Team Branding Comparison', value='tab-2'),
        dcc.Tab(label='Factors Associated with Good Branding', value='tab-3')
    ]),
    html.Div(id='tabs-content')


])

# callback for choosing tabs
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return  html.Div([ 
            # create row of cards with best branded teams
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # best branded team by viewers
                                        html.Img(src = Image.open('logos/UA.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('Avg Viewers: '), #id='placeholder2'),
                                            ], style={'textAlign': 'center'})
                                        ])
                                ),])
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # best branded team by ratings
                                        html.Img(src = Image.open('logos/UA.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('Avg Ratings: ' ), #id='placeholder3'),
                                            ], style={'textAlign': 'center'})
                                        ])
                                    ),
                                ]) 
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # best branded team by %capacity
                                        html.Img(src = Image.open('logos/UGA.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('Avg Stadium Capacity: '), #id='placeholder4'),
                                            ], style={'textAlign': 'center'})
                                        ])
                                    ),
                                ]) 
                        ], width=4),
                    ], align='center'), 
                    html.Br(),
                    
                    # graphs with average stadium capacity and viewership per team
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
        
    # layout for 2nd tab, team comparisons
    elif tab == 'tab-2':
        return html.Div([ 
            # create row of cards with best branded teams
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # choose 1st team to compare
                                        html.Img(src = Image.open('logos/SEC.png'), 
                                                 style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.Div([
                                                html.H4('Choose A Team: ' ),
                                                dcc.Dropdown(options = team_names_dict, 
                                                             value = 'Tennessee',
                                                             id = "dropdown1"
                                                    ),
                                                ], style={'textAlign': 'center'})
                                            ])
                                        ])
                                ),])
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # choose 2nd team to compare
                                        html.Img(src = Image.open('logos/SEC.png'), 
                                                 style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('Choose A Team: ' ),
                                            dcc.Dropdown(options = team_names_dict, 
                                                         value = 'Alabama',
                                                         id = "dropdown2"
                                                        ),
                                            ], style={'textAlign': 'center'})
                                        ])
                                    ),
                                ]) 
                        ], width=6),
                    ], align='center'), 
                    html.Br(),
                    
                    # time series of viewership for both teams
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id = 'time-series1'),
                            dcc.Graph(id = 'time-series3') 
                        ], width=6),
                        dbc.Col([
                            dcc.Graph(id = 'time-series2'),
                            dcc.Graph(id = 'time-series4')
                        ], width=6),
                    ], align='center'), 
                    html.Br(),     
                ]), color = 'light'
            )
        ])
    elif tab == 'tab-3':
        return html.Div([ 
            # create row of cards with best branded teams
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # best branded team by viewers
                                        html.Img(src = Image.open('logos/SEC.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('Weighted Rank of Matchup'), #id='placeholder2'),
                                            html.H6('*Teams Outside the Top 25: Ranking = 26')
                                            ], style={'textAlign': 'center'})
                                        ])
                                ),])
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # best branded team by ratings
                                        html.Img(src = Image.open('logos/SEC.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('TV Network Comparison' ), #id='placeholder3'),
                                            ], style={'textAlign': 'center'})
                                        ])
                                    ),
                                ]) 
                        ], width=4),
                        dbc.Col([
                            html.Div([
                                dbc.Card(
                                    dbc.CardBody([
                                        # best branded team by %capacity
                                        html.Img(src = Image.open('logos/SEC.png'), style={'height':'8%', 'width':'8%', 'display': 'inline-block'}),
                                        html.Div([
                                            html.H4('Individual Team Rankings'), #id='placeholder4'),
                                            html.H6('*Teams Outside the Top 25: Ranking = 26')
                                            ], style={'textAlign': 'center'})
                                        ])
                                    ),
                                ]) 
                        ], width=4),
                        
                    ], align='center'), 
                    html.Br(),
                    
                    # graphs with average stadium capacity and viewership per team
                    dbc.Row([
                        dbc.Col([
                            draw_graph(id='summed_ranks',figure=summed_ranks)  
                        ], width=4),
                        dbc.Col([
                            draw_graph(id='networks',figure=networks) 
                        ], width=4),
                        dbc.Col([
                            draw_graph(id='ranks_views',figure=ranks_views) 
                        ], width=4),
                    ], align='center'), 
                    html.Br(),     
                ]), color = 'light'
            )
        ])

@app.callback(
    Output('time-series1','figure'),
    Output('time-series3', 'figure'),
    Input('dropdown1','value')
)
def update_graph(team1):
    # time series of percent capacity
    fig1 = go.Figure(
            go.Scatter(x=MERGED[(MERGED['homename'] == team1) |( MERGED['visname'] == team1)]['date'],
                        y=MERGED[(MERGED['homename'] == team1) |( MERGED['visname'] == team1)]['Percent_of_Capacity']
                            #markers = dict(color='navy')
                            ))
    
    fig1.update_xaxes(range=[0,51.5], title_text = 'Date of Game')
    fig1.update_yaxes(title_text = 'Percent Capacity')
    fig1.update_layout(title_text='Percent Capacity per Game')
    fig1.update_yaxes(range=[.4,1.3])
    
    # get logo in background of graph
    image = choose_logo(team1) 
    fig1.add_layout_image(
        dict(
            source= Image.open(image),
            xref="x",
            yref="y",
            x=.4,
            y=1.3,
            sizex=45,
            sizey=.9,
            sizing = 'stretch',
            opacity=0.3,
            layer="below")
        )
    fig1.update_layout(template="plotly_white") 
    
    # time series of viewers
    fig3 = go.Figure(
        go.Scatter(x=MERGED[(MERGED['homename'] == team1) |( MERGED['visname'] == team1)]['date'],
                    y=MERGED[(MERGED['homename'] == team1) |( MERGED['visname'] == team1)]['VIEWERS']
                        #markers = dict(color='navy')
                        ))
    
    fig3.update_xaxes(range=[0,51.5], title_text = 'Date of Game')
    fig3.update_yaxes(title_text = 'Number of Viewers')
    fig3.update_layout(title_text='Viewership per Game')
    fig3.update_yaxes(range=[0 ,15000000])
    
    # get logo in background of graph
    image = choose_logo(team1) 
    fig3.add_layout_image(
        dict(
            source= Image.open(image),
            xref="x",
            yref="y",
            x=0,
            y=15000000,
            sizex=45,
            sizey=15000000,
            sizing = 'stretch',
            opacity=0.3,
            layer="below")
        )
    fig3.update_layout(template="plotly_white") 
    return fig1, fig3


@app.callback(
    Output('time-series2','figure'),
    Output('time-series4', 'figure'),
    Input('dropdown2','value')
)
def update_graph(team2):
    fig2 = go.Figure(
            data=go.Scatter(x=MERGED[(MERGED['homename'] == team2) |( MERGED['visname'] == team2)]['date'],
                            y=MERGED[(MERGED['homename'] == team2) |( MERGED['visname'] == team2)]['Percent_of_Capacity']
                            #markers = dict(color='navy')
                            ))
    fig2.update_xaxes(range=[0,51.5], title_text = 'Date of Game')
    fig2.update_yaxes(title_text = 'Percent Capacity')
    fig2.update_layout(title_text='Percent Capacity per Game')
    fig2.update_yaxes(range=[.4,1.3])
    
    # get logo in background of graph
    image = choose_logo(team2)
    fig2.add_layout_image(
        dict(
            source= Image.open(image),
            xref="x",
            yref="y",
            x=.4,
            y=1.3,
            sizex=45,
            sizey=.9,
            sizing = 'stretch',
            opacity=0.3,
            layer="below")
        )
    fig2.update_layout(template="plotly_white") 
    
    fig4 = go.Figure(
    go.Scatter(x=MERGED[(MERGED['homename'] == team2) |( MERGED['visname'] == team2)]['date'],
                y=MERGED[(MERGED['homename'] == team2) |( MERGED['visname'] == team2)]['VIEWERS']
                    #markers = dict(color='navy')
                    ))
    
    fig4.update_xaxes(range=[0,51.5], title_text = 'Date of Game')
    fig4.update_yaxes(title_text = 'Number of Viewers')
    fig4.update_layout(title_text='Viewership per Game')
    fig4.update_yaxes(range=[0 ,15000000])
    
    # get logo in background of graph
    image = choose_logo(team2) 
    fig4.add_layout_image(
        dict(
            source= Image.open(image),
            xref="x",
            yref="y",
            x=0,
            y=15000000,
            sizex=45,
            sizey=15000000,
            sizing = 'stretch',
            opacity=0.3,
            layer="below")
        )
    fig4.update_layout(template="plotly_white") 
    return fig2, fig4

if __name__ == '__main__':
    app.run_server(debug=True) 
    

