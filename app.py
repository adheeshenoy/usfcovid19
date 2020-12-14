import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from flask_caching import Cache
import layouts
import data
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import graphGenerator as gg
from datetime import datetime, timedelta
import helper_functions as hf
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

server = Flask(__name__)

#TODO Add error bars

# from fbprophet import Prophet

# Function names follow snake case
# Variable names and Callbacks are camel case
# Ids use hypens

app = dash.Dash(
    __name__,
    server= server,
    external_stylesheets=[dbc.themes.FLATLY, '/assets/stylesheet.css'],
    meta_tags=[{
        "name":
        "viewport",
        "content":
        "width=device-width, initial-scale=1, minimum-scale = 1, maximum-scale=1"
    }],
    suppress_callback_exceptions=True)

# server = app.server

app.title = 'USF Covid 19'
app._favicon = '/assets/favicon.ico'

# SQLAlchemy
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config['SQLALCHEMY_DATABASE_URI'] = 'Postgres URI'
db = SQLAlchemy(app.server)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False), layouts.navbar,
    dcc.Store(id='data', data=data.__get_data().to_json()),
    html.Div(layouts.USFLayout, id='page-content'), layouts.footer
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def page(pathname):
    if pathname == '/table-header':
        return layouts.table_layout
    else:
        return layouts.USFLayout


@app.callback([Output('table', 'columns'),
               Output('table', 'data')], [Input('data', 'data')])
def updateDataTable(data):
    try:
        df = hf.string_to_df(data).iloc[::-1]
        data_table = hf.generate_data_table_information(df)
        return data_table[0], data_table[1]
    except:
        raise PreventUpdate


@app.callback([
    Output('tampa-card-totalcases', 'children'),
    Output('tampa-card-health-totalcases', 'children'),
    Output('st-pete-card-totalcases', 'children'),
    Output('tampa-card-update', 'children'),
    Output('tampa-card-health-update', 'children'),
    Output('st-pete-card-update', 'children'),
    Output('sarasota-card-totalcases', 'children'),
    Output('sarasota-card-update', 'children'),
], [Input('data', 'data')])
def updateCards(data):
    try:
        df = hf.string_to_df(data)

        # Get for each location
        dfByLocation = hf.get_df_by_location(df)

        # Get total cases for each location
        totalCasesTampa, totalCasesStPete, totalCasesHealth, totalCasesSarasota = hf.get_total_cases_by_location(
            dfByLocation)

        # Get daily cases for each location
        dailyCasesTampa, dailyCasesStPete, dailyCasesHealth, dailyCasesSarasota = hf.get_daily_cases_by_location(
            dfByLocation)

        return totalCasesTampa + ' cases', totalCasesHealth + ' cases',totalCasesStPete + ' cases',\
            hf.create_daily_cases_string(dailyCasesTampa), hf.create_daily_cases_string(dailyCasesHealth),\
            hf.create_daily_cases_string(dailyCasesStPete), totalCasesSarasota + ' cases',\
            hf.create_daily_cases_string(dailyCasesSarasota)
            
    except Exception as e:
        print('updateCards: ', e)
        raise PreventUpdate


@app.callback([
    Output('daily-bar-graph', 'figure'),
    Output('total-scatter-graph', 'figure')
], [Input('data', 'data'),
    Input('graph_type','value')])
def create_general_graphs(data, graphType):
    df = hf.string_to_df(data)
    prediction_df = pd.read_sql_table('prediction', con=db.engine)
    df['dates'] = df['dates'].apply(lambda date: datetime.strptime(date, "%B %d %Y"))

    location_list = hf.get_daily_cases_by_location(hf.get_df_by_location(df))
    prediction_list = hf.get_prediction_by_location(prediction_df)

    return dict(data=gg.generate_daily_bar_graph(location_list),
                layout=gg.generate_bar_layout('Daily Cases on USF Campuses', 'group')), \
           dict(data=gg.generate_total_scatter(graphType, location_list, prediction_list),
                layout=gg.general_graph_layout('Total Cases USF Campuses'))


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback([
    Output('employee-student-daily-graph', 'figure'),
    Output('employee-student-box', 'figure'),
    Output('employee-student-pie', 'figure'),
    Output('employee-student-total-graph', 'figure'),
    Output('general-overview', 'children'),
    Output('general-daily-average', 'children'),
    Output('collapse-text', 'children')
], [Input('data', 'data'),
    Input('general-tabs', 'active_tab')])
def campus_graphs(data, active_tab):
    try:
        # Converting string to data frame
        return tab_content(hf.string_to_df(data), active_tab)

    except Exception as e:
        print('Campus Graph: ', e)
        raise PreventUpdate


def tab_content(df, active_tab):
    new_df = df[df['locations'] == active_tab]
    new_df['dates'] = new_df['dates'].apply(
        lambda date: datetime.strptime(date, '%B %d %Y'))
    employeeAvg, studentAvg = hf.get_daily_average(new_df)
    result, status, mostRecent, lastValue = hf.get_percent(new_df)
    occupationList = hf.get_df_by_occupation(new_df)
    student = new_df[new_df['occupations'] == 'Student']
    employee = new_df[new_df['occupations'] == 'Employee']
    return dict(data = gg.generate_employee_student_daily_graph(occupationList), layout = gg.generate_bar_layout(f'Student Vs. Employee Daily Cases (USF {active_tab})', 'stack')),\
        dict(data = gg.generate_box_plot(occupationList), layout = gg.general_graph_layout(f'Box Plot For Daily Cases Per Occupation (USF {active_tab})')),\
        dict(data = gg.generate_pie_plot(occupationList), layout = gg.general_graph_layout(f'Total Cases Percentage Per Occupation (USF {active_tab})')),\
        dict(data = gg.generate_employee_student_total_graph(occupationList), layout = gg.general_graph_layout(f'Student Vs. Employee Total Cases (USF {active_tab})')),\
        f'The USF {active_tab} has seen a {result:.2%} {status} in cases in the last two weeks. The number of cases went from {lastValue} to {mostRecent}.',\
        hf.create_avg_string(employeeAvg, studentAvg, active_tab), hf.generate_collapse(active_tab)


app.scripts.config.serve_locally = False
app.scripts.append_script({
    'external_url':
    'https://cdn.jsdelivr.net/gh/adheeshenoy/usfcovid19/async_src.js'
})
app.scripts.append_script({
    'external_url':
    'https://cdn.jsdelivr.net/gh/adheeshenoy/usfcovid19/gtag.js'
})

if __name__ == '__main__':
    app.run_server(debug=True)