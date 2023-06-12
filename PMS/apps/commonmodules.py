from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app

navlink_style = {
    'color': '#fff',
    'margin-right': '1em'
}

hidden_style = {
    'color': '#fff',
    'margin-right': '1em',
    'display' : 'none',
}
navbar = dbc.Navbar(
    [
        html.A(
            dbc.NavbarBrand("DIEOR PMS", className="ml-2", 
            style={'margin-right': '2em','margin-left': '1em', 'font-size':'3em'}),
            href="/home",
        ),
        dbc.NavLink("Home", href="/home", style=navlink_style),
        dbc.NavLink("Faculty", href="/faculty", id="faculty_nav", style=hidden_style),
        dbc.NavLink("Accountabilities", href="/props", id="accountabilities_nav", style=hidden_style),
        dbc.NavLink("Account", href="/account", id="account_nav", style=hidden_style),
        dbc.NavLink("Admin", href="/account/create", id="admin_nav", style=hidden_style),
        dbc.NavLink("Login", href="/login", id="login_nav", style=navlink_style),
    ],
    dark=True,
    color='blue'
)