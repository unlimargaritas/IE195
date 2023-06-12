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

import os
import base64
import random

from app import app
from apps import dbconnect as db

layout = html.Div(
    [ 
        html.Div(
            [
            dcc.Store(id='propprof_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2("Property Details"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Label("Property ID", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_id", placeholder="Enter Property ID"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),      
        dbc.Row(
            [
                dbc.Label("Description", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_desc", placeholder="Enter description"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Quantity", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_qty", placeholder="Enter quantity"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Unit", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_unit", placeholder="Enter unit"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),  
        dbc.Row(
            [
                dbc.Label("Date Acquired", width=2),
                dbc.Col(     
                    html.Div(
                        dcc.DatePickerSingle(
                            id='propprof_purch_date',
                        ),
                        className="dash-bootstrap"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Quantity Cost", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_purch_amt", placeholder="Enter quantity cost per unit"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),   
        dbc.Row(
            [
                dbc.Label("Total Cost", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_total_purch_amt", placeholder="Enter total cost"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),   
        dbc.Row(
            [
                dbc.Label("Officer ID", width=2),
                dbc.Col(
                   dcc.Dropdown(
                        id='employeeprof_id',
                        clearable=True,
                        searchable=True
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),   
        dbc.Row(
            [
                dbc.Label("Status", width=2),
                dbc.Col(
                    dcc.Dropdown(
                        ['Borrowed', 'Returned'], 'Borrowed',
                        id='propprof_stat',
                        clearable=True,
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("Category", width=2),
                dbc.Col(
                    dcc.Dropdown(
                        ['Airconditioner', 'ICT Equipment', 'Office Equipment', 'General Service', 'Others'], 'Airconditioner',
                        id='propprof_category',
                        clearable=True,
                        searchable=True
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ), 
        dbc.Row(
            [
                dbc.Label("Location", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_location", placeholder="Enter Location"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Label("PAR", width=2),
                dbc.RadioItems(
                    options=[
                        {"label": "Personal PAR", "value": 1},
                        {"label": "Mother PAR", "value": 2},
                    ],
                    value=1,
                    id="propprof_par_type",
                    inline=True,
                ),
            ],
            className="mb-3",
        ),                    
        dbc.Row(
            [
                dbc.Label("Remarks", width=2),
                dbc.Col(
                    dbc.Input(
                        type="text", id="propprof_remarks", placeholder="Remarks"
                    ),
                    width=6,
                ),
            ],
            className="mb-3",
        ),  
        dbc.Row(
            [
                dbc.Label("Receipt", width=2),
                dbc.Col(
                    dcc.Upload(dbc.Button('Upload File'), id="propprof_receipt"),
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
                            id='propprof_removerecord',
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
            id = 'propprof_removerecord_div'
        ),
        html.Hr(),
        dbc.Button('Submit', color="success", id='propprof_submitbtn', n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader("Saving Progress"),
                dbc.ModalBody("tempmessage", id='propprof_feedback_message'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Okay", id="propprof_closebtn", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="propprof_modal",
            is_open=False
        ),
    ],
)


@app.callback(
    [
        Output('propprof_toload', 'data'),
        Output('propprof_removerecord_div', 'style'),
        Output('employeeprof_id', 'options')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search')
    ]
)
def propprof_editprocess(pathname, search):
    print("Search:", search)
    if pathname == '/props/props_profile':
        sql = """
            select employee_fn, employee_ln, employee_id
            from employees 
        """

        values = []
        cols = ['employeefn', 'employeeln', 'employeeid']
        df = db.querydatafromdatabase(sql, values, cols)

        employee_options = []
        for index in range(df.shape[0]):
            employee_options.append({ 'label' : df['employeeln'][index] + ', '+ df['employeefn'][index], 'value' : df['employeeid'][index]})
    
        parsed = urlparse(search)
        mode = parse_qs(parsed.query)['mode'][0] 
        print(f"Value of 'mode': {mode}")

        to_load = 1 if mode == 'edit' else 0

        removerecord_div = None if to_load else {'display': 'none'}
    else:
        raise PreventUpdate
    
    return [to_load, removerecord_div, employee_options]

@app.callback(
    [
        Output('propprof_modal', 'is_open'),
        Output('propprof_feedback_message','children'),
        Output('propprof_closebtn','href')
    ],
    [
        Input('propprof_submitbtn', 'n_clicks'),
        Input('propprof_closebtn','n_clicks')
    ],
    [
        State('propprof_desc', 'value'),
        State('propprof_qty', 'value'),
        State('propprof_unit', 'value'),
        State('propprof_purch_date', 'date'),
        State('propprof_purch_amt', 'value'),
        State('propprof_total_purch_amt', 'value'),
        State('employeeprof_id', 'value'),
        State('propprof_stat', 'value'),
        State('propprof_category', 'value'),
        State('propprof_remarks', 'value'),
        State('propprof_receipt', 'contents'),
        State('propprof_receipt', 'filename'),
        State('url', 'search'),
        State('propprof_removerecord', 'value'),
        State('propprof_location', 'value'),
        State('propprof_par_type', 'value')
        
    ]
)

def propprof_submitprocess(submitbtn, closebtn,
                                desc, qty, unit, purch_date, purch_amt, total_purch_amt, employee_id, stat, category, remarks, receipt_file, receipt_name, location, par_type,
                                search, removerecord):
    print("Search:", search)
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        print("Event ID:", eventid)
        openmodal = False
        feedbackmessage = ''
        okay_href = None
        if eventid == "propprof_submitbtn" and submitbtn:
            print("Submit button clicked")
            openmodal = True
            inputs = [
                desc
                # qty,
                # unit,
                # purch_date,
                # purch_amt,
                # total_purch_amt,
                # employee_id,
                # stat,
                # remarks,
                # receipt_file,
                # receipt_name,
                # location
                # par_type
            ]

            if not all(inputs):
                feedbackmessage = "Please supply all inputs."
            elif len(desc) > 256:
                feedbackmessage = "Property desc is too long (length=256)."
            else:
                # source https://docs.faculty.ai/user-guide/apps/examples/dash_file_upload_download.html

                if receipt_file:
                    data = receipt_file.encode("utf8").split(b";base64,")[1]
                    receipt_name = str(random.randrange(1,10000)) + receipt_name 
                    with open(os.path.join("assets/", receipt_name), "wb") as fp:
                        fp.write(base64.decodebytes(data))
                
                parsed = urlparse(search)
                mode = parse_qs(parsed.query).get('mode', [None])[0]
                print(f"Value of 'mode': {mode}")

                if mode == 'add':
                    sqlcode = """ INSERT INTO properties(
                        prop_desc,
                        prop_qty,
                        prop_unit,
                        prop_purch_date,
                        prop_purch_amt,
                        prop_total_purch_amt,
                        employee_id,
                        prop_stat,
                        prop_category,
                        prop_remarks,
                        rcpt_name,
                        prop_delete_ind,
                        prop_location,
                        prop_par_type
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    values = [desc, qty, unit, purch_date, purch_amt, total_purch_amt, employee_id, stat, category, remarks, receipt_name, False, location, par_type]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "prop has been saved."
                    okay_href = '/props'

                elif mode == 'edit':
                    parsed = urlparse(search)
                    propid = parse_qs(parsed.query)['id'][0]
                    sqlcode = """UPDATE properties
                    SET
                        prop_desc = %s,
                        prop_qty = %s,
                        prop_unit = %s,
                        prop_purch_date = %s,
                        prop_purch_amt = %s,
                        prop_total_purch_amt = %s,
                        employee_id = %s,
                        prop_stat = %s,
                        prop_category = %s,
                        prop_remarks = %s,
                        rcpt_name = %s,
                        prop_delete_ind = %s
                        prop_location = %s,
                        prop_par_type = %s
                    WHERE
                        prop_id = %s
                    """

                    to_delete = bool(removerecord)

                    values = [desc, qty, unit, purch_date, purch_amt, total_purch_amt, employee_id, stat, category, remarks, receipt_name, to_delete, location, par_type, propid]
                    db.modifydatabase(sqlcode, values)
                    feedbackmessage = "prop has been updated."
                    okay_href = '/props'


                else:
                    raise PreventUpdate
                

        elif eventid == 'propprof_closebtn' and closebtn:
            print("Close button clicked")
            pass

        else:
            raise PreventUpdate

        return [openmodal, feedbackmessage, okay_href]

    else:
        print("No callback context triggered")
        raise PreventUpdate

@app.callback(
    [
        Output('propprof_id', 'value'),
        Output('propprof_desc', 'value'),
        Output('propprof_qty', 'value'),
        Output('propprof_unit', 'value'),
        Output('propprof_purch_date', 'date'),
        Output('propprof_purch_amt', 'value'),
        Output('propprof_total_purch_amt', 'value'),
        Output('employeeprof_id','value'),
        Output('propprof_stat', 'value'),
        Output('propprof_category', 'value'),
        Output('propprof_remarks', 'value'),
        Output('propprof_location', 'value'),
        Output('propprof_par_type', 'value'),
    ],
    [
        Input('propprof_toload', 'modified_timestamp')
    ],
    [
        State('propprof_toload', 'data'),
        State('url', 'search')
    ]
)
def loadpropdetails(timestamp, to_load, search):
    if to_load == 1:
        sql = """SELECT prop_desc, prop_qty, prop_unit, prop_purch_date, prop_purch_amt, prop_total_purch_amt, employee_id, prop_stat, prop_category, prop_remarks, prop_location, prop_par_type
        FROM properties
        WHERE prop_id = %s
        """

        parsed = urlparse(search)
        propid = parse_qs(parsed.query)['id'][0]

        val = [propid]
        colnames = ['desc', 'qty', 'unit', 'purch_date', 'purch_amt', 'total_purch_amt', 'employee_id','stat', 'category', 'remarks', 'location', 'par_type']

        df = db.querydatafromdatabase(sql, val, colnames)

        desc = df['desc'][0]
        qty = df['qty'][0]
        unit = df['unit'][0]
        purch_date = df['purch_date'][0]
        purch_amt = df['purch_amt'][0]
        total_purch_amt = df['total_purch_amt'][0]
        employee_id = df['employee_id'][0]
        stat = df['stat'][0]
        category = df['category'][0]
        remarks = df['remarks'][0]
        location = df['location'][0]
        par_type = df['par_type'][0]

        return [propid, desc, qty, unit, purch_date, purch_amt, total_purch_amt, employee_id, stat, category, remarks, location, par_type]
    else:
        raise PreventUpdate
                            
