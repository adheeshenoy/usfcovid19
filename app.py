import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from flask_caching import Cache
import layouts
import data
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import ast
import pandas as pd
import graphGenerator as gg
from datetime import datetime, timedelta

# Things to do
# Talk about combining usf health with tampa
# Talk about adding stats

# Function names have _
# Variable names and Callbacks are camelcase
# Id is -

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, '/assets/stylesheet.css'])

server = app.server

# cache = Cache(app.server,
#               config={
#                   'CACHE_TYPE': 'filesystem',
#                   'CACHE_DIR': 'cache-directory',
#               })

app.layout = html.Div(
    [dcc.Store(id='data', data=data.__get_data()), layouts.USFLayout])

# Functions and Callbacks


def __string_to_df(string):
    '''Helper function that returns the dataframe from a string'''
    if isinstance(string, str):
        return pd.DataFrame(ast.literal_eval(string))


# Rafael add day here as a parameter
def __get_percent(df, days=10):
    '''Helper function that returns percentage of increase in cases in the specified
    number of days. 
    Output: result (percentage), status(increase or decrease), mostRecent value,
    Last updated value.'''
    lastTenDays = df.groupby('dates', sort=False, as_index=False).sum()
    lastTenDays['cases'] = lastTenDays['cases'].cumsum()
    lastTenDays = lastTenDays.tail(11)
    lastValue = 0
    while True:
        dayLimit = datetime.strftime(datetime.today() - timedelta(days=days),
                                     '%Y-%m-%d')
        if not lastTenDays[lastTenDays['dates'] == dayLimit].empty:
            lastValue = int(
                lastTenDays[lastTenDays['dates'] == dayLimit]['cases'])
            break
        else:
            days += 1

    mostRecent = int(lastTenDays['cases'].iloc[-1])
    result = ((mostRecent - lastValue) / lastValue)
    status = 'increase'

    if result < 0:
        status = 'decrease'
        result *= -1

    return result, status, mostRecent, lastValue


def __get_daily_average(df):
    temp = df.groupby('occupations').mean()
    return temp['cases'][0], temp['cases'][1]


def __create_avg_string(employeeAvg, studentAvg, campus='Tampa'):
    ratio = studentAvg / employeeAvg
    return f'For any given day, on average, {ratio:.2} times the number of students are tested positive compared to USF {campus} employees.'\
            if(ratio != 1.0) else f'For any given day, on average, the same number of students are tested positive as USF {campus} employees.'


@app.callback([
    Output('tampa-card-totalcases', 'children'),
    Output('tampa-card-health-totalcases', 'children'),
    Output('tampa-card-update', 'children'),
    Output('st-pete-card-totalcases', 'children'),
    Output('st-pete-card-update', 'children'),
    Output('table', 'columns'),
    Output('table', 'data')
], [Input('data', 'data')])
def updateCards(data):
    try:
        df = __string_to_df(data)
        tampa = df[df['locations'] == 'Tampa']
        health = df[df['locations'] == 'Health']
        totalCasesHealth = str(health['cases'].sum())
        totalCasesTampa = str(tampa['cases'].sum())
        stPete = df[df['locations'] == 'St. Pete']
        totalCasesStPete = str(stPete['cases'].sum())
        dailyCasesTampa = tampa.groupby('dates', sort=False).sum()
        dailyCasesStPete = stPete.groupby('dates', sort=False).sum()
        df['dates'] = df['dates'].apply(lambda date: date.title())
        return 'USF Tampa : ' + totalCasesTampa + ' cases','USF Health : ' + totalCasesHealth + ' cases', str(dailyCasesTampa['cases'][-1]) + ' case(s) (Date: ' + \
            str(tampa['dates'][-1]).title() + ')','USF St. Petersburg : ' + totalCasesStPete + ' cases',\
            str(dailyCasesStPete['cases'][-1]) + ' case(s) (Date: ' +\
            str(stPete['dates'][-1]).title() + ')',\
            [{'name': i.title() , 'id': i} for i in df.columns],\
            df.to_dict('records')
    except Exception as e:
        print('updateCards: ', e)
        raise PreventUpdate


@app.callback([
    Output('daily-bar-graph', 'figure'),
    Output('total-scatter-graph', 'figure')
], [Input('data', 'data')])
def create_general_graphs(data):
    try:
        df = __string_to_df(data)
        tampa = df[(df['locations'] == 'Tampa') |
                   (df['locations'] == 'Health')].groupby(
                       'dates', sort=False, as_index=False).sum()
        stPete = df[df['locations'] == 'St. Pete'].groupby(
            'dates', sort=False, as_index=False).sum()
        tampa['dates'] = tampa['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))
        stPete['dates'] = stPete['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))
        return dict(data = gg.generate_daily_bar_graph(tampa,stPete), layout = gg.general_bar_layout('Daily Cases on USF Campuses')),\
            dict(data = gg.generate_total_scatter_graph(tampa,stPete), layout = gg.general_graph_layout('Total Cases on USF Campuses'))
    except Exception as e:
        print(e)
        raise PreventUpdate


@app.callback([
    Output('tampa-employee-student-daily-graph', 'figure'),
    Output('tampa-employee-student-health-box', 'figure'),
    Output('tampa-employee-student-health-pie', 'figure'),
    Output('tampa-employee-student-total-graph', 'figure'),
    Output('tampa-overview', 'children'),
    Output('health-overview', 'children'),
    Output('tampa-daily-average', 'children')
], [Input('data', 'data')])
def tampa_campus_graphs(data):
    try:
        df = __string_to_df(data)
        df['dates'] = df['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))

        health = df[df['locations'] == 'Health']

        df = df[(df['locations'] == 'Tampa')]

        tampaEmployeeAvg, tampaStudentAvg = __get_daily_average(df)
        # healthEmployeeAvg = health['cases'].mean()

        tampaResult, tampaStatus, tampaMostRecent, tampaLastValue = __get_percent(
            df)
        healthResult, healthStatus, healthMostRecent, healthLastValue = __get_percent(
            health)

        student = df[df['occupations'] == 'Student']
        employee = df[df['occupations'] == 'Employee']

        return dict(data = gg.generate_employee_student_daily_graph(student, employee, health), layout = gg.stacked_graph_layout('Student Vs. Employee Daily Cases (USF Tampa)')),\
            dict(data = gg.generate_box_plot(student, employee, health), layout = gg.general_graph_layout('Quartile Representation Of Daily Cases Per Occupation (USF Tampa)')),\
            dict(data = gg.generate_pie_plot(student, employee, health), layout = gg.general_graph_layout('Total Cases Percentage Per Occupation (USF Tampa)')),\
            dict(data = gg.generate_employee_student_total_graph(student, employee, health), layout = gg.general_graph_layout('Student Vs. Employee Total Cases (USF Tampa)')),\
            f'The USF Tampa campus has seen a {tampaResult:.2%} {tampaStatus} in cases in the last ten days. The number of cases went from {tampaLastValue} to {tampaMostRecent}.',\
            f'USF Health has seen a {healthResult:.2%} {healthStatus} in cases in the last ten days. The number of cases went from {healthLastValue} to {healthMostRecent}.',\
            __create_avg_string(tampaEmployeeAvg, tampaStudentAvg)

    except Exception as e:
        print('campus_graph: ', e)
        raise PreventUpdate


@app.callback([
    Output('st-pete-employee-student-daily-graph', 'figure'),
    Output('st-pete-employee-student-health-box', 'figure'),
    Output('st-pete-employee-student-health-pie', 'figure'),
    Output('st-pete-employee-student-total-graph', 'figure'),
    Output('st-pete-overview', 'children'),
    Output('st-pete-daily-average', 'children')
], [Input('data', 'data')])
def st_pete_campus_graphs(data):
    try:
        df = __string_to_df(data)
        df = df[(df['locations'] == 'St. Pete')]
        df['dates'] = df['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))

        result, status, mostRecent, lastValue = __get_percent(df)
        EmployeeAvg, StudentAvg = __get_daily_average(df)

        student = df[df['occupations'] == 'Student']
        employee = df[df['occupations'] == 'Employee']

        show_cases = '' if (
            lastValue == mostRecent
        ) else f' The number of cases went from {lastValue} to {mostRecent}.'

        return dict(data = gg.generate_employee_student_daily_graph(student, employee), layout = gg.stacked_graph_layout('Student Vs. Employee Daily Cases (USF St. Pete)')),\
            dict(data = gg.generate_box_plot(student, employee), layout = gg.general_graph_layout('Quartile Representation Of Daily Cases Per Occupation (USF St. Pete)')),\
            dict(data = gg.generate_pie_plot(student, employee), layout = gg.general_graph_layout('Total Cases Percentage Per Occupation (USF St. Pete)')),\
            dict(data = gg.generate_employee_student_total_graph(student, employee), layout = gg.general_graph_layout('Student Vs. Employee Total Cases (USF St. Pete)')),\
            f'The USF St. Petersburg campus has seen a {result:.2%} {status} in cases in the last ten days.' + show_cases,\
            __create_avg_string(EmployeeAvg, StudentAvg, 'St. Petersburg')
    except Exception as e:
        print('campus_graph: ', e)
        raise PreventUpdate


@app.callback(
    Output("tampa-collapse", "is_open"),
    [Input("tampa-collapse-button", "n_clicks")],
    [State("tampa-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("st-pete-collapse", "is_open"),
    [Input("st-pete-collapse-button", "n_clicks")],
    [State("st-pete-collapse", "is_open")],
)
def st_pete_toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# app.scripts.config.serve_locally = False
# app.scripts.append_script({
#     'external_url': 'https://www.googletagmanager.com/gtag/js?id=UA-172379483-1'
# })
# app.scripts.append_script({
#     'external_url': 'https://cdn.jsdelivr.net/gh/lppier/lppier.github.io/gtag.js'
# })

if __name__ == '__main__':
    app.run_server(debug=True)