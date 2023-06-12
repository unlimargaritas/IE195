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

layout = html.Div(
    [ 
        html.Div(
            [
            dcc.Store(id='facultyprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Faculty Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Last Name", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="facultyprof_last_name", placeholder="Enter Last Name"
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
                        type="text", id="facultyprof_first_name", placeholder="Enter First Name"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Role", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="facultyprof_role", placeholder="Enter role"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        html.Div(
                dbc.Row(
                [
                    dbc.Label("Wish to delete?", width=2),
                    dbc.Col(
                        dbc.Checklist(
                            id='facultyprof_removerecord',
                            options=[
                                {
                                'label': "Mark for Deletion",
                                'value': 1
                                }
                            ],
                            style={'fontWeight':'bold'},
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            id = 'facultyprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='facultyprof_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody("tempmessage", id='facultyprof_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="facultyprof_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="facultyprof_modal",
            is_open=False
        ),
    ],
)
@app.callback(
    [
        Output('facultyprof_toload', 'data'),
        Output('facultyprof_removerecord_div', 'style')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search')
    ]
)

def facultyprof_editprocess(pathname, search):
    if pathname == '/faculty/faculty_profile':
        sql = """
        """

        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0]
        to_load = 1 if mode == 'edit' else 0

        removerecord_div = None if to_load else {'display': 'none'}

    else:
        raise PreventUpdate
    
    return [to_load, removerecord_div]  

@app.callback(
    [
        Output('facultyprof_modal', 'is_open'),
        Output('facultyprof_feedback_message', 'children'),
        Output('facultyprof_closebtn', 'href')
    ],
    [
        Input('facultyprof_submitbtn', 'n_clicks'),
        Input('facultyprof_closebtn', 'n_clicks')
    ],
    [
        State('facultyprof_last_name','value'),
        State('facultyprof_first_name', 'value'),
        State('facultyprof_role', 'value'),
        State('url', 'search'),
        State('facultyprof_removerecord', 'value')
    ]
)

def facultyprof_submitprocess(submitbtn, closebtn,
                                lastname, firstname, role,
                                search, removerecord):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "facultyprof_submitbtn" and submitbtn:
            openmodal = True
            inputs = [
                lastname,
                firstname,
                role
            ]
            if not all(inputs):
                feedbackmessage = "Please supply all inputs."
            elif len(lastname)>256:
                feedbackmessage = "Title is too long (length=256)."
            elif len(firstname)>256:
                feedbackmessage = "Title is too long (length=256)."

            else:
                parsed = urlparse(search)
                mode = parse_qs(parsed.query)['mode'][0]
                if mode == 'add': 
                    sqlcode = """ INSERT INTO employees(
                        employee_ln,
                        employee_fn,
                        employee_role,
                        employee_delete_ind
                    )
                    VALUES (%s, %s, %s, %s)
                    """
                    values = [lastname, firstname, role, False]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Faculty has been saved."
                    okay_href = '/faculty'

                elif mode == 'edit':
                    parsed = urlparse(search)
                    facultyid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """UPDATE employees
                    SET
                        employee_ln = %s,
                        employee_fn = %s,
                        employee_role = %s,
                        employee_delete_ind = %s
                    WHERE
                        employee_id = %s
                    """

                    to_delete = bool(removerecord)

                    values = [lastname, firstname, role, to_delete, facultyid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "Faculty has been updated."
                    okay_href = '/faculty'

                else:
                    raise PreventUpdate

        elif eventid == 'facultyprof_closebtn' and closebtn:
            pass

        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]
    else:
        raise PreventUpdate



@app.callback(
    [
        Output('facultyprof_last_name', 'value'),
        Output('facultyprof_first_name', 'value'),
        Output('facultyprof_role', 'value'),
    ],
    [
        Input('facultyprof_toload', 'modified_timestamp')
    ],
    [
        State('facultyprof_toload', 'data'),
        State('url', 'search')
    ]
)

def loadfacultydetails(timestamp, to_load, search):
    if to_load == 1:
        sql = """SELECT employee_ln, employee_fn, employee_role
        FROM employees
        WHERE employee_id = %s
        """

        parsed = urlparse(search)
        facultyid = parse_qs(parsed.query)['id'][0]

        val = [facultyid]
        colnames = ['last name','first name', 'role']

        df = db.querydatafromdatabase(sql, val, colnames)

        name = df['last name'][0]
        contact = df['first name'][0]
        role = df['role'][0]

        return [name, contact, role]

    else:
        raise PreventUpdate