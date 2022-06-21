from dash import html
import dash
from dash_labs.plugins.pages import register_page

register_page(__name__, path="/404")


layout = html.H1("Error 404 : Page Not Found (custom)")
