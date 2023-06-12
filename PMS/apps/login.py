import hashlib

import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

navlink_style = {
    'color': '#fff',
    'margin-right': '1em'
}

hidden_style = {
    'color': '#fff',
    'margin-right': '1em',
    'display' : 'none',
}

layout = html.Div(
    [
        html.H2('Welcome! Please Login'),
        html.Hr(),
        dbc.Alert('Username or password is incorrect.', color="danger", id='login_alert',
                  is_open=False),
        dbc.Row(
            [
                dbc.Label("Username", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="login_username", placeholder="Enter username"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Password", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="login_password", placeholder="Enter password"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Button('Login', color="success", id='login_loginbtn'),
        html.Hr(),
        html.A('Signup for New Users', href='/signup'),
    ]
)


@app.callback(
    [
        Output('login_alert', 'is_open'),
        Output('currentuserid', 'data'),
        Output('currentrole', 'data'),
        Output('currentemployeeid', 'data'),
    ],
    [
        Input('login_loginbtn', 'n_clicks'),
    ],
    [
        State('login_username', 'value'),
        State('login_password', 'value'),   
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'), 
    ]
)
def loginprocess(loginbtn, username, password,
                 sessionlogout, currentuserid):
    openalert = False
    
    if loginbtn and username and password:
        sql = """SELECT user_id, user_admin, user_dep_head
        FROM users
        WHERE 
            user_name = %s AND
            user_password = %s AND
            NOT user_delete_ind"""
        
        
        encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest() 
        
        values = [username, encrypt_string(password)]
        cols = ['userid', 'useradmin', 'userdephead']
        df = db.querydatafromdatabase(sql, values, cols)
        
        if df.shape[0]: 
            currentuserid = df['userid'][0]
            currentrole = 1 if df['useradmin'][0] else (2 if df['userdephead'][0] else 0)
            currentemployeeid = 0
            
            sql = """SELECT employee_id
                    FROM employees
                    WHERE 
                        user_id = %s"""

            values = [str(currentuserid)]
            cols = ['employeeid']
            df = db.querydatafromdatabase(sql, values, cols)

            if df.shape[0]:      
                currentemployeeid = df['employeeid'][0]
        else:
            currentuserid = 0
            currentrole = 0
            currentemployeeid = 0
            openalert = True
        
    else:
        raise PreventUpdate
    
    return [openalert, currentuserid, currentrole, currentemployeeid]

@app.callback(
    [
        Output('url', 'pathname'),
        Output('login_nav', 'children'),
        Output('login_nav', 'href'),
        Output('account_nav', 'style'),
        Output('admin_nav', 'style'),
        Output('accountabilities_nav', 'style'),
        Output('faculty_nav', 'style'),

    ],
    [
        Input('currentuserid', 'modified_timestamp'),
    ],
    [
        State('currentuserid', 'data'), 
        State('currentrole', 'data'), 
    ]
)
def routelogin(logintime, userid, role):
    ctx = callback_context
    if ctx.triggered:
        if userid:
            url = '/home'
            login = 'Logout'
            login_url = '/logout'
            account_style = navlink_style
            accountabilities_style = navlink_style
            faculty_style = navlink_style
            if role:
                admin_style = navlink_style
            else:
                admin_style = hidden_style
        else:
            url = '/home'
            login = 'Login'
            login_url = '/login'
            account_style = hidden_style
            admin_style = hidden_style
            accountabilities_style = hidden_style
            faculty_style = hidden_style
    else:
        raise PreventUpdate
    return [url, login, login_url, account_style, admin_style, accountabilities_style, faculty_style]