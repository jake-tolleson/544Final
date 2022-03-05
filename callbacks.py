from dash import Input, Output, callback

@callback(
    Output('page-1-display-value', 'children'))
def display_value(value):
    pass

@callback(
    Output('page-2-display-value', 'children'))
def display_value(value):
    pass