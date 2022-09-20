import dash
import base64
from flask import Flask, send_from_directory
from urllib.parse import quote as urlquote
from dash import html, Input, Output
import dash_labs as dl
import dash_bootstrap_components as dbc

from dash_bootstrap_templates import ThemeSwitchAIO
url_theme1 = dbc.themes.BOOTSTRAP
url_theme2 = dbc.themes.DARKLY

server = Flask(__name__)
app = dash.Dash(
    __name__, 
    plugins=[dl.plugins.pages],
    server=server,
    external_stylesheets=[dbc.themes.DARKLY],
)
app.title="TimeSeries Analyzer"
app._favicon = ("./assets/favicon.ico")

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Timeseries", href="/ts")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("GitHub", href="https://github.com/Dodalpaga/TimeSeries-Analysis-Dash-App", target="_blank"),
                dbc.DropdownMenuItem("Contact", href="https://dodalpaga.github.io/Porfolio/", target="_blank"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="TimeSeries Analyzer",
    brand_href="/",
    color="primary",
    dark=True,
)

app.layout = html.Div(
    [
        navbar,
        dl.plugins.page_container,
        html.Div(
            ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]),
            style={'position': 'fixed', 'bottom': '1%', 'left': '1%'},
        )
    ]
)

UPLOAD_DIRECTORY = "uploads/"
RESULT_DIRECTORY = "results/"
import os
if not os.path.exists(UPLOAD_DIRECTORY):
    os.system("pwd")
    os.system("mkdir {}".format(UPLOAD_DIRECTORY))
    
if not os.path.exists(RESULT_DIRECTORY):
    os.system("pwd")
    os.system("mkdir {}".format(RESULT_DIRECTORY))

@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files

def result_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(RESULT_DIRECTORY):
        path = os.path.join(RESULT_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    [Output("file-list", "children"),Output("results-list", "children")],
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)

def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    files.sort()
    results = result_files()
    results.sort()
    if len(files) == 0:
        return [html.Li("No uploads yet!")],[html.Li("No results yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files],[html.Li(file_download_link(filename)) for filename in results]
    


@server.route("/")
def index():
    return 'Hello Flask app'

@server.route("/github")
def github():
    return 'Hello Flask app'

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)