from dash import dcc
from dash import html, ALL
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State
from apps import dbconnect as db

from app import app

import json, os

normal_style = {
    'display' : 'unset'
}

hidden_style = {
    'display' : 'none',
}

layout = html.Div(
    [
        html.H2("Accountabilities"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Property Records")),
                dbc.CardBody(
                    [
                        dbc.Button("Add Property", color="primary", href = '/props/props_profile?mode=add', id='add_prop_btn', style=hidden_style),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Property",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search via:", width=2),
                                        dbc.RadioItems(
                                            options=[
                                                {"label": "Category", "value": 'prop_category'},
                                                {"label": "Status", "value": 'prop_stat'},
                                                {"label": "Faculty", "value": 'employee_ln'},
                                            ],
                                            value="prop_category",
                                            id="search_filter",
                                            inline=True,
                                        ),
            
                                        dbc.Label("Search Category", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='prop_category_filter',
                                                placeholder='Enter Category Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for property records",
                                    id="prop_proplist"
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("Receipt"),
                dbc.ModalBody(
                    [
                        html.Img(id='prop_receipt_image', style={'width' : '466px', 'height' : '400px'},)
                    ],
                )
            ],
            id="prop_receipt_modal",
            is_open=False
        ),
    ]
)

#restricting searchfilters
@app.callback(
        [
            Output('search_filter','options'),
        ],
        [
            Input('url', 'pathname'),
        ],
        [
            State('currentrole', 'data'), 
            State('currentuserid', 'data'),
            State('currentemployeeid', 'data'),
        ]

)
def updatesearchfilteroptions(pathname, role, user, employeeid):
    if pathname == '/props':
        if not(role):
            new_options =[
                {"label": "Category", "value": 'prop_category'},
                {"label": "Status", "value": 'prop_stat'},
            ]
            return [new_options]
        else:
            PreventUpdate
    else:
        PreventUpdate

@app.callback(
    [
        Output('prop_proplist', 'children'),
        Output('prop_receipt_image', 'src'),
        Output('prop_receipt_modal', 'is_open'),
        Output('add_prop_btn', 'style'),
    ],
    [
        Input('url', 'pathname'),
        Input('prop_category_filter', 'value'),
        Input({'type':'btn_created','index': ALL}, 'n_clicks'),
    ],
    [
        State('currentrole', 'data'), 
        State('currentuserid', 'data'),
        State('currentemployeeid', 'data'),
        State('search_filter', 'value')
    ]
 )

def updatepropertylist(pathname, searchterm, btnpressed, role, user, employeeid, searchfilter):
    if pathname == '/props':
        receipt_name = ""
        openmodal = False

        style = hidden_style
        if role:
            style = normal_style          


        if (len(set(btnpressed)) > 1):
            ctx = dash.ctx
            receipt_name = json.loads(ctx.triggered[0]['prop_id'].split('.n_clicks')[0])['index']
            openmodal = True


        sql = """select p.prop_id, prop_desc, prop_purch_amt, prop_qty, prop_total_purch_amt, prop_purch_date, prop_stat, prop_category, prop_ret_date, o.employee_ln, rcpt_name, prop_location, prop_par_type
            from properties p LEFT JOIN employees o ON o.employee_id = p.employee_id
            where not prop_delete_ind
        """
        if searchfilter == 'prop_stat' and searchterm == 'condemned':
            sql += "AND p.prop_stat = 'condemned'"
        else:
            sql += "AND (p.prop_stat != 'ondemned' OR p.prop_stat IS NULL)"

        val = []
        colnames = ['Property ID', 'Description', 'Purchase Amount', 'Quantity', 'Total Purchase Amount', 'Purchase Date', 'Status', 'Category', 'Return Date', 'Employee Last Name', 'Receipt', 'Location', 'PAR']
        if searchterm:
            sql += "AND "+ searchfilter + " ILIKE %s"
            val += [f"%{searchterm}%"]

        if not(role):
            sql += "AND o.employee_id = %s"
            val += [employeeid]

        
        sql += "order by prop_modified_date DESC LIMIT 30"

        
        properties = db.querydatafromdatabase(sql, val, colnames)

        if properties.shape[0]:
            buttons = []
            receipts = []
            if role:
                for propid in properties['Property ID']:
                    buttons += [
                        html.Div(
                            dbc.Button('Edit/Delete', href=f"/props/props_profile?mode=edit&id={propid}",
                                        size='sm', color='warning'),
                            style={'text-align': 'center'}
                        )
                    ]
                properties['Edit/Delete Record'] = buttons

            for rcptname in properties['Receipt']:
                if rcptname:
                    receipts += [
                        html.Div(
                            dbc.Button('Link', id={'type':'btn_created', 'index': rcptname},
                                        size='sm', color='warning'),
                            style={'text-align': 'center'}
                        )
                    ]
                else:
                    receipts += [
                        html.Div()
                    ]

            properties['Receipt'] = receipts

            properties.drop('Property ID', axis=1, inplace=True)

            table = dbc.Table.from_dataframe(properties, striped = True, bordered = True, hover = True, size = 'sm')
            return [table, app.get_asset_url(receipt_name), openmodal, style]

        else:
            return ["There are no records that match the search term.", "", False, style]
    
    else:
        raise PreventUpdate