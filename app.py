import dash
from dash import html, dcc, Input, Output, State, dash_table, callback_context
import pandas as pd
import plotly.express as px
import os

# CSV file name
filename = "tech_data.csv"
technologies = ["Ansible","Python" ,"CI/CD", "Jenkins", "AWS", "OCI"]

if not os.path.exists(filename):
    pd.DataFrame(columns=["Name"] + technologies).to_csv(filename, index=False)

def generate_figure(dataframe):
    if dataframe.empty:
        return px.bar(title="Tech Knowledge Distribution")
    tech_counts = dataframe[technologies].sum().reset_index()
    tech_counts.columns = ["Technology", "UserCount"]
    return px.bar(tech_counts, x="Technology", y="UserCount", title="Tech Knowledge Distribution")

app = dash.Dash(__name__)
app.title = "Tech Knowledge Tracker"

#app.layout = html.Div(style={"textAlign": "center", "backgroundColor": "#f0f8ff", "padding": "20px"}, children=[
app.layout = html.Div(style={"textAlign": "center", "backgroundColor": "#D8BFD8", "padding": "20px"}, children=[
    dcc.Location(id="url"),

    #html.H1("Hello Learners!", style={"color": "#2c3e50"}),
    #html.H1("Enter Name & Select Skills", style={"color": "#2c3e50"}),
    html.H1("Enter Name & Select Skills Learners", style={"color": "#2c3e50"}),

    html.Div([
        dcc.Input(id="username", type="text", placeholder="Enter your name", style={"marginBottom": "10px"}),
        html.Div([
            dcc.Checklist(
                id="tech_select",
                options=[{"label": tech, "value": tech} for tech in technologies],
                style={"textAlign": "left"},
                labelStyle={"display": "block"}
            )
        ], style={"width": "200px", "margin": "0 auto"}),
        html.Button("Submit", id="submit_btn", n_clicks=0),
    ], style={"marginBottom": "20px"}),

    dcc.Graph(id="bar_chart"),

    html.Div(id="msg", style={"color": "green", "marginTop": "10px"}),

    html.H3("Current CSV Data", style={"marginTop": "40px", "color": "#2c3e50"}),
    dash_table.DataTable(
        id='csv_table',
        columns=[{"name": col, "id": col} for col in ["Name"] + technologies],
        data=[],
        style_table={"overflowX": "auto", "marginTop": "10px"},
        style_cell={"textAlign": "center", "padding": "5px"},
        style_header={"backgroundColor": "#cce5ff", "fontWeight": "bold"}
    )
])

@app.callback(
    Output("bar_chart", "figure"),
    Output("csv_table", "data"),
    Output("msg", "children"),
    Input("submit_btn", "n_clicks"),
    Input("url", "pathname"),
    State("username", "value"),
    State("tech_select", "value")
)
def handle_data(n_clicks, pathname, name, selected_techs):
    ctx = callback_context
    df = pd.read_csv(filename)

    if ctx.triggered and ctx.triggered[0]['prop_id'].startswith('submit_btn') and name and selected_techs:
        # Remove old entry if exists
        df = df[df["Name"] != name]
        new_row = {tech: 1 if tech in selected_techs else 0 for tech in technologies}
        new_row["Name"] = name
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(filename, index=False)
        msg = f"Thanks, {name}! Your response has been recorded."
    else:
        msg = ""

    return generate_figure(df), df.to_dict("records"), msg

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9071)

