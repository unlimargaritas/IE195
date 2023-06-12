from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import webbrowser

from app import app
from apps import commonmodules as cm
from apps import home, login, signup
from apps.faculty import faculty_home, faculty_profile
from apps.props import props_home, props_profile
from apps.account import account_profile, account_creation

CONTENT_STYLE = {
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

app.layout = html.Div(
    [
        
        dcc.Location(id='url', refresh=True),
        
        dcc.Store(id='sessionlogout', data=False, storage_type='session'),
        
        
        dcc.Store(id='currentuserid', data=0, storage_type='session'),
        
        
        dcc.Store(id='currentrole', data=0, storage_type='session'),

        dcc.Store(id='currentemployeeid', data=0, storage_type='session'),
        
        html.Div(
            cm.navbar,
            id='navbar_div'
        ),
        
        
        html.Div(id='page-content', style=CONTENT_STYLE),
    ]
)



@app.callback(
    [
        Output('page-content', 'children'),
        Output('navbar_div', 'style'),
        Output('currentuserid', 'clear_data'),
        Output('currentrole', 'clear_data'),
        Output('currentemployeeid', 'clear_data'),
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)
def displaypage(pathname, sessionlogout, currentuserid):
    
    
    ctx = dash.callback_context
    if ctx.triggered:
       
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate
                
    if pathname in ['/', '/home']:
            returnlayout = home.layout
    elif pathname == '/faculty':  
            returnlayout = faculty_home.layout
    elif pathname == '/faculty/faculty_profile':  
            returnlayout = faculty_profile.layout
    elif pathname == '/login':  
            returnlayout = login.layout
    elif pathname == '/account':  
            returnlayout = account_profile.layout
    elif pathname == '/account/create':  
        returnlayout = account_creation.layout
    elif pathname == '/props':  
            returnlayout = props_home.layout
    elif pathname == '/props/props_profile':  
            returnlayout = props_profile.layout
    elif pathname == '/signup':  
            returnlayout = signup.layout
    elif pathname == '/logout':
            returnlayout = home.layout
            sessionlogout = True
    else: 
            returnlayout = home.layout
        
    navbar_div = {'display': 'unset'}
    return [returnlayout, navbar_div, sessionlogout, sessionlogout, sessionlogout]


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=True)
