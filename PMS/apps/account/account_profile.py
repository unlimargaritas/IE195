from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State
from apps import dbconnect as db

from app import app

import hashlib

normal_style = {
    'display' : 'unset'
}

hidden_style = {
    'display' : 'none',
}

# LANDING PAGE TO 'ACCOUNT MODULE' (page 9 in mock)
# EDIT BUTTON FOR PASSWORD ONLY?

layout = html.Div(
    [
        html.Div(
            [
            dcc.Store(id='accountprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Account"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Hello!"), id="current_account_name"),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Label("Username:", width=2),
                                dbc.Col(
                                    html.P(
                                        "", id="current_account_username", 
                                    ),
                                    width=6,
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Label("Role: ", width=2),
                                dbc.Col(
                                    html.P("", id="current_account_role", 
                                    ),
                                    width=6,
                                ),

                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Label("Password: ", width=2),
                                dbc.Col(
                                    html.P("", id="current_account_pw", 
                                    ),
                                    width=6,
                                ),
                            ]

                        ),
                        dbc.Button("Transfer Headship", color="Secondary", id="account_transfer", n_clicks=0, style=hidden_style),
                        dbc.Button("Update Password", color="Secondary", id="current_account_updatepw", n_clicks=0),
                        dbc.Modal(
                            [
                                dbc.ModalHeader("Update Password"),
                                dbc.ModalBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Label("New Password: ", width=2),
                                                dbc.Input(
                                                    type="text", id="current_account_new_pw", placeholder="Enter new password",
                                                ),
                                            ],

                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Confirm New Password: ", width=2),
                                                dbc.Input(
                                                    type="text", id="current_account_confirm_pw", placeholder="Retype new password"
                                                ),
                                                
                                            ],
                                        ),
                                        dbc.Row(id="current_account_feedback_message")
                                    ],
                                ),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Update Password", id="account_updatebtn", className="ms-auto", n_clicks=0, href="/account",
                                    )
                                ),
                            ],
                            id="account_update_modal",
                            is_open=False
                        ),

                        dbc.Modal(
                            [
                                dbc.ModalHeader("Transfer Department Head"),
                                dbc.ModalBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Label("Transfer to: ", width=2),
                                                dcc.Dropdown(
                                                        id='employee_id',
                                                        clearable=True,
                                                        searchable=True
                                                ),
    
                                            ],

                                        ),
                                        dbc.Row(id="account_transfer_feedback_message")
                                    ],
                                ),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Confirm Transfer", id="account_transferbtn", className="ms-auto", n_clicks=0, href="/logout",
                                    )
                                ),
                            ],
                            id="account_transfer_modal",
                            is_open=False
                        ),
                    ]
                ),

            ]
        )
    ]
)

@app.callback(
    [
        Output('accountprof_toload', 'data'),
    ],
    [
        Input('url', 'pathname'),
    ],
)
def accountprof_editprocess(pathname):
    if pathname == "/account":
        to_load = 1
    else:
        raise PreventUpdate
    return [to_load]



@app.callback(
    [
        Output('current_account_username', 'children'),
        Output('current_account_role', 'children'),
        Output('current_account_pw', 'children'),
        Output('account_transfer', 'style'),
        Output('employee_id', 'options'),
    ],
    [
        Input('accountprof_toload', 'modified_timestamp'),
    ],
    [
        Input('accountprof_toload', 'data'),
        State('currentuserid', 'data'), 
        State('currentemployeeid', 'data'), 
    ]
)
def loadprofile(pathname, to_load, userid, employeeid):
    if to_load:
        sql = """SELECT user_name, user_faculty, user_admin, user_dep_head, user_password
                    FROM users
                    WHERE 
                    user_id = %s
            """

        values = [userid]
        cols = ['username', 'faculty', 'admin', 'dephead', 'password']
        df = db.querydatafromdatabase(sql, values, cols)

        username = df['username'][0]
        role = df['faculty'][0].astype(int) * "Faculty" + df['admin'][0].astype(int) * "Admin" + df['dephead'][0].astype(int) * "Department Head" 
        password = df['password'][0]

        style = normal_style if role == "Department Head" else hidden_style

        sql = """
            select employee_fn, employee_ln, employee_id
            from employees 
            where employee_id != %s
        """

        values = [employeeid]
        cols = ['employeefn', 'employeeln', 'employeeid']
        df = db.querydatafromdatabase(sql, values, cols)

        employee_options = []
        for index in range(df.shape[0]):
            employee_options.append({ 'label' : df['employeeln'][index] + ', '+ df['employeefn'][index], 'value' : df['employeeid'][index]})

        return [username, role, password, style, employee_options]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('account_update_modal', 'is_open'),
        Output('current_account_feedback_message', 'children'),
    ],
    [
        Input('current_account_updatepw', 'n_clicks'),
        Input('account_updatebtn', 'n_clicks'),
    ],
    [
        State('currentuserid', 'data'),
        State('currentrole', 'data'),
        State('current_account_new_pw', 'value'),
        State('current_account_confirm_pw', 'value'),
    ]
)
def change_password_modal(modal, updatepw, userid, role, password, confirmpassword):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        if eventid == 'current_account_updatepw':
            openmodal = True

        elif eventid == 'account_updatebtn':
            if password == confirmpassword:
                sql = """UPDATE users
                        SET
                            user_password = %s
                        WHERE
                            user_id = %s
                """

                encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest() 

                values = [encrypt_string(password), userid]
                db.modifydatabase(sql, values)

                feedbackmessage = 'Password has been changed'
            else:
                feedbackmessage = 'Passwords do not match'

            openmodal = True
    
        return [openmodal, feedbackmessage]
    else: 
        raise PreventUpdate

@app.callback(
    [
        Output('account_transfer_modal', 'is_open'),
        Output('account_transfer_feedback_message', 'children'),
    ],
    [
        Input('account_transfer', 'n_clicks'),
        Input('account_transferbtn', 'n_clicks'),
    ],
    [
        State('currentuserid', 'data'),
        State('currentrole', 'data'),
        State('employee_id', 'value'),
        State('currentemployeeid', 'data'),
    ]
)
def transfer_modal(modal, transferacc, userid, role, employeeid, deptheadid):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        if eventid == 'account_transfer':
            openmodal = True

        elif eventid == 'account_transferbtn':
            sql = """SELECT user_id
            FROM employees
            WHERE 
            employee_id = %s
            """

            values = [employeeid]
            cols = ['userid']
            df = db.querydatafromdatabase(sql, values, cols)

            employeeuserid = df['userid'][0].astype(str)

            sql = """UPDATE users
                    SET
                        user_faculty = 'True',
                        user_dep_head= 'False'
                    WHERE
                        user_id = %s;

                    UPDATE users
                    SET 
                        user_faculty = 'False',
                        user_dep_head = 'True'
                    WHERE 
                        user_id = %s;



                    UPDATE employees
                    SET
                        employee_role = 'Faculty'
                    WHERE
                        employee_id = %s;

                    UPDATE employees
                    SET
                        employee_role = 'Department Head'
                    WHERE
                        employee_id = %s;
            """

            values = [userid, employeeuserid, deptheadid, employeeid]
            db.modifydatabase(sql, values)

            feedbackmessage = 'Department Head role transfer complete'

            openmodal = True
    
        return [openmodal, feedbackmessage]
    else: 
        raise PreventUpdate