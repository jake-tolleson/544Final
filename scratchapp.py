from dash import Dash, dcc, html, Input, Output, callback

from layouts import Page1Layout, Page2Layout
#import callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == 'Page2':
         return Page2Layout
    else:
         return Page1Layout

if __name__ == '__main__':
    app.run_server(debug=True)