import hashlib

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

layout = html.Div(
    [
        html.H2('Register New User'),
        html.Hr(),
        dbc.Alert('Please supply details.', color="danger", id='signup_alert',
                  is_open=False),
        dbc.Row(
            [
                dbc.Label("Username", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="signup_username", placeholder="Enter a username"
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
                        type="password", id="signup_password", placeholder="Enter a password"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        
        dbc.Row(
            [
                dbc.Label(" Confirm Password", width=2),
                dbc.Col(
                    dbc.Input(
                        type="password", id="signup_passwordconf", placeholder="Re-type the password"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Button('Sign up', color="success", id='singup_signupbtn'),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("User Saved")),
                dbc.ModalBody("User has been saved", id='signup_confirmation'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", href='/'
                    )
                ),
            ],
            id="signup_modal",
            is_open=False,
        ),
    ]
)



@app.callback(
    [
        Output('singup_signupbtn', 'disabled'),
    ],
    [
        Input('signup_password', 'value'),
        Input('signup_passwordconf', 'value'),
    ]
)
def deactivatesignup(password, passwordconf):
    
  
    enablebtn = password and passwordconf and password == passwordconf

    return [not enablebtn]



@app.callback(
    [
        Output('signup_alert', 'is_open'),
        Output('signup_modal', 'is_open')   
    ],
    [
        Input('singup_signupbtn', 'n_clicks')
    ],
    [
        State('signup_username', 'value'),
        State('signup_password', 'value')
    ]
)
def saveuser(loginbtn, username, password):
    openalert = openmodal = False
    if loginbtn:
        if username and password:
            sql = """INSERT INTO users (user_name, user_password, user_faculty, user_admin, user_delete_ind)
            VALUES (%s, %s, %s, %s, %s)"""  
            
       
            encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()  
            
            values = [username, encrypt_string(password), False, False, False]
            db.modifydatabase(sql, values)
            
            openmodal = True
        else:
            openalert = True
    else:
        raise PreventUpdate

    return [openalert, openmodal]