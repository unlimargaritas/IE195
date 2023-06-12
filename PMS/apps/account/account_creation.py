from datetime import date
from sre_parse import State
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.parse import urlparse, parse_qs

from app import app
from apps import dbconnect as db

import hashlib

# FORM TO CREATE NEW ACCOUNTS (page 10 in mock)
# ONLY ADMIN HAS ACCESS TO

layout = html.Div(
    [
        html.H2("Account Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Employee Number", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="employee_id", placeholder="Enter Officer ID"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Username", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="employee_username", placeholder="Enter Username"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("First Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="employee_first_name", placeholder="Enter First Name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Middle Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="employee_middle_name", placeholder="Enter Middle Name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Last Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="employee_last_name", placeholder="Enter Last Name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Email", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="employee_email_add", placeholder="Enter email address"
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
                        type="text", id="employee_pw", placeholder="Enter password"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Role:", width=2),
                dbc.RadioItems(
                    options=[
                        {"label": "Admin", "value": 1},
                        {"label": "Faculty", "value": 2},
                        {"label": "Department Head", "value": 3},
                    ],
                    value=1,
                    id="employee_role",
                    inline=True,
                ),
            ]
        ),

        html.Hr(),
        dbc.Button('Submit', color="secondary", id='account_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("New Account Created"),
                dbc.ModalBody("tempmessage", id='account_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Done", id="account_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="account_modal",
            is_open=False
        ),
    ],
)

@app.callback(
    [
        Output('account_modal', 'is_open'),
        Output('account_feedback_message', 'children'),
        Output('account_closebtn', 'href'),
        
    ],
    [
        Input('account_submitbtn', 'n_clicks'),
        Input('account_closebtn', 'n_clicks'),
    ],
    [
        State('employee_id','value'),
        State('employee_username', 'value'),
        State('employee_first_name', 'value'),
        State('employee_middle_name', 'value'),
        State('employee_last_name', 'value'), 
        State('employee_email_add', 'value'), 
        State('employee_pw', 'value'), 
        State('employee_role', 'value'), 
    ]
)

def account_submitprocess(submitbtn, closebtn,
                                userid, username, firstname,
                                middlename, lastname, emailadd, password, role):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "account_submitbtn" and submitbtn:
            openmodal = True
            inputs = [
                username,
                firstname,
                middlename,
                lastname,
                emailadd,
                password,
                role,
            ]
            if not all(inputs):
                feedbackmessage = "Please supply all inputs."
            
            else:
                sqlcode = """ INSERT INTO users(
                        user_name,
                        user_fn,
                        user_mn,
                        user_ln,
                        user_email,
                        user_password,
                        user_faculty,
                        user_admin,
                        user_dep_head,
                        user_delete_ind
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest() 

    
                faculty = True if role == 2 else False
                admin = True if role == 3 else False
                dep_head = True if role == 3 else False
                values = [username, firstname, middlename, lastname, emailadd, encrypt_string(password), faculty, admin, dep_head, False]
                db.modifydatabase(sqlcode, values)

                sql = """SELECT user_id
                FROM users
                WHERE 
                user_name = %s
                """

                values = [username]
                cols = ['userid']
                df = db.querydatafromdatabase(sql, values, cols)

                userid = df['userid'][0].astype(str)
                
                if faculty or role == 3:

                    sqlcode = """ INSERT INTO employees(
                        employee_ln,
                        employee_fn,
                        employee_role,
                        employee_delete_ind,
                        user_id
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    role = "Department Head" if role == 3 else "Faculty"

                    values = [lastname, firstname, role, False, userid]
                    db.modifydatabase(sqlcode, values)

                feedbackmessage = "Account has been saved."
                okay_href = '/account/create'

        elif eventid == 'account_closebtn':
            pass
        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]
    else:
        raise PreventUpdate