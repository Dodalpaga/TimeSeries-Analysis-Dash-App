import dash
import base64
from flask import Flask, send_from_directory
from urllib.parse import quote as urlquote
from dash import Dash, dcc, html, Input, Output
import dash_labs as dl
import dash_bootstrap_components as dbc


server = Flask(__name__)
app = dash.Dash(
    __name__, 
    plugins=[dl.plugins.pages],
    server=server,
    external_stylesheets=[dbc.themes.CERULEAN],
)
app.title="TimeSeries Analyzer"

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Bar Chart", href="/bar")),
        dbc.NavItem(dbc.NavLink("Histogram", href="/hist")),
        dbc.NavItem(dbc.NavLink("Heatmap", href="/heat")),
        dbc.NavItem(dbc.NavLink("Timeseries", href="/ts")),
        dbc.NavItem(dbc.NavLink("Test", href="/test")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("GitHub", href="/github"),
                dbc.DropdownMenuItem("Contact", href="/contact"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NavbarSimple",
    brand_href="/",
    color="primary",
    dark=True,
)

app.layout = dbc.Container(
    [navbar,dl.plugins.page_container],
    fluid=True,
)

UPLOAD_DIRECTORY = "uploads/"
import os
if not os.path.exists(UPLOAD_DIRECTORY):
    os.system("pwd")
    os.system("mkdir {}".format(UPLOAD_DIRECTORY))

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


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)

def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]
    


@server.route("/")
def index():
    return 'Hello Flask app'


# Run the server
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)