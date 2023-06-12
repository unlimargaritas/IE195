from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State
from apps import dbconnect as db

from app import app

layout = html.Div(
    [
        html.H2("Faculty"),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H4("Faculty Records")),
                dbc.CardBody(
                    [
                        # dbc.Button("Add Faculty", color="primary", href = '/faculty/faculty_profile?mode=add'),
                        html.Hr(),
                        html.Div(
                            [
                                html.H6("Find Faculty",style={'fontweight':'bold'}),
                                html.Hr(),
                                dbc.Row(
                                    [
                                        dbc.Label("Search Faculty Last Name", width=2),
                                        dbc.Col(
                                            dbc.Input(
                                                type='text',
                                                id='faculty_name_filter',
                                                placeholder='Enter Faculty Name'
                                            ),
                                            width=6,
                                        ),
                                    ],
                                className='mb-3',
                                ),
                                html.Div(
                                    "This will contain the table for faculty records",
                                    id="faculty_facultylist"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
@app.callback(
    [
        Output('faculty_facultylist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('faculty_name_filter', 'value'),
    ],
    [
        State('currentrole', 'data'), 
    ]
 )
def updatefacultylist(pathname, searchterm, role):
    if pathname == '/faculty':
        sql = """select o.employee_ln, o.employee_fn, o.employee_role, o.employee_id, COUNT(p.employee_id)
            from employees o LEFT JOIN properties p ON o.employee_id = p.employee_id
            where not employee_delete_ind
        """
        val = []
        colnames = ['Last name', 'First name', 'Role', 'ID', 'Accountabilities count']
        if searchterm:
            sql += "AND employee_ln ILIKE %s"
            val += [f"%{searchterm}%"]

        sql += "GROUP BY o.employee_id ORDER BY LOWER(o.employee_ln)"
        
        employees = db.querydatafromdatabase(sql, val, colnames)
        if employees.shape[0]:
            buttons = []
            if role:
                for employeesid in employees['ID']:
                    buttons += [
                        html.Div(
                            dbc.Button('Edit/Delete', href=f"/faculty/faculty_profile?mode=edit&id={employeesid}",
                                        size='sm', color='warning'),
                            style={'text-align': 'center'}
                        )
                    ]
                
                employees['Edit/Delete Record'] = buttons

            employees.drop('ID', axis=1, inplace=True)

            table = dbc.Table.from_dataframe(employees, striped = True, bordered = True, hover = True, size = 'sm')
            return [table]

        else:
            return ["There are no records that match the search term."]
    
    else:
        raise PreventUpdate
                            