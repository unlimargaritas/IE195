from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output, State

from app import app

from apps import dbconnect as db

layout = html.Div(
    [
        html.H2('DIEOR Property Management System'),
        html.Hr(),
        html.Div(
            [
                html.Span("Hello there!"),
                html.Br(),
                html.Br(),
                html.Span("Contact support if you need assistance!",
                style={'font-style':'italic'}),
            ]
        ),
    ],
)