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

# Function names follow snake case
# Variable names and Callbacks are camel case
# Ids use hypens

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, '/assets/stylesheet.css'],
    meta_tags=[{
        "name":
        "viewport",
        "content":
        "width=device-width, initial-scale=1, minimum-scale = 1, maximum-scale=1"
    }],
)

server = app.server

app.title = 'USF Covid 19'
app._favicon = '/assets/favicon.ico'

# cache = Cache(app.server,
#               config={
#                   'CACHE_TYPE': 'filesystem',
#                   'CACHE_DIR': 'cache-directory',
#               })

app.layout = html.Div(
    [dcc.Store(id='data', data=data.__get_data()), layouts.USFLayout])

# Functions and Callbacks

def __string_to_df(string):
    '''Helper function that converts a string into a dataframe'''
    if isinstance(string, str):
        return pd.DataFrame(ast.literal_eval(string))


def __get_percent(df, days=14):
    '''Helper function that returns percentage of increase in cases in the specified
    number of days. 
    Output: result (percentage), status(increase or decrease), mostRecent value,
    Last updated value.'''
    lastTenDays = df.groupby('dates', sort=False, as_index=False).sum()
    lastTenDays['cases'] = lastTenDays['cases'].cumsum()
    lastTenDays = lastTenDays.tail(days+1)
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
    '''returns the daily average for each occupation'''
    temp = df.groupby('occupations').mean()
    return temp['cases'][0], temp['cases'][1]


def __create_avg_string(employeeAvg, studentAvg, campus='Tampa'):
    '''returns a string that specifies the daily average for student vs employees'''
    ratio = studentAvg / employeeAvg
    return f'Per day, on average, {ratio:.2} times the number of students are tested positive compared to USF {campus} employees.'\
            if(ratio != 1.0) else f'Per day, on average, the same number of students are tested positive as USF {campus} employees.'

def __get_df_by_location(df, locations = ['Tampa','St. Pete', 'Health']):
    '''Divides a dataframe containing multiple locations based on location'''
    dfs = []
    for location in locations:
        dfs.append(df[df['locations'] == location])
    return dfs

def __get_total_cases_by_location(dfByLocation):
    '''Returns a list of total cases for each location'''
    totalCases = []
    for df in dfByLocation:
        totalCases.append(str(df['cases'].sum()))
    return totalCases

def __get_daily_cases_by_location(dfByLocation):
    '''Returns a list of daily cases for each location'''
    dailyCases = []
    for df in dfByLocation:
        dailyCases.append(df.groupby('dates', sort=False, as_index = False).sum())
    return dailyCases

def __create_daily_cases_string(dailyCases):
    '''Returns a string to print for daily cases'''
    text = str(dailyCases['cases'].iloc[-1]) + ' cases (' if dailyCases['cases'].iloc[-1] > 1 else\
        str(dailyCases['cases'].iloc[-1]) + ' case (' 
    return text + str(dailyCases['dates'].iloc[-1]) + ')'

def __generate_data_table_information(df):
    '''Returns the information needed for generating the data table'''
    return ([{'name': i, 'id': i} for i in df.columns],df.to_dict('records'))

@app.callback([
    Output('tampa-card-totalcases', 'children'),
    Output('tampa-card-health-totalcases', 'children'),
    Output('st-pete-card-totalcases', 'children'),
    Output('tampa-card-update', 'children'),
    Output('tampa-card-health-update', 'children'),
    Output('st-pete-card-update', 'children'),
    Output('table', 'columns'),
    Output('table', 'data')
], [Input('data', 'data')])
def updateCardsAndDataTable(data):
    try:
        df = __string_to_df(data)

        # Get for each location
        dfByLocation = __get_df_by_location(df)

        # Get total cases for each location
        totalCasesTampa, totalCasesStPete, totalCasesHealth = __get_total_cases_by_location(dfByLocation)

        # Get daily cases for each location
        dailyCasesTampa, dailyCasesStPete, dailyCasesHealth = __get_daily_cases_by_location(dfByLocation)

        # df['dates'] = df['dates'].apply(lambda date: date.title())
        data_table = __generate_data_table_information(df)
    
        return totalCasesTampa + ' cases', totalCasesHealth + ' cases',totalCasesStPete + ' cases',\
            __create_daily_cases_string(dailyCasesTampa), __create_daily_cases_string(dailyCasesHealth),\
            __create_daily_cases_string(dailyCasesStPete),\
            data_table[0], data_table[1]
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
        
        
        tampa = df[(df['locations'] == 'Tampa')].groupby(
                       'dates', sort=False, as_index=False).sum()
        health = df[(df['locations'] == 'Health')].groupby(
                       'dates', sort=False, as_index=False).sum()
        stPete = df[df['locations'] == 'St. Pete'].groupby(
            'dates', sort=False, as_index=False).sum()
        tampa['dates'] = tampa['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))
        health['dates'] = health['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))
        stPete['dates'] = stPete['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))
        return dict(data = gg.generate_daily_bar_graph(tampa,stPete, health), layout = gg.general_bar_layout('Daily Cases on USF Campuses')),\
            dict(data = gg.generate_total_scatter_graph(tampa,stPete, health), layout = gg.general_graph_layout('Total Cases on USF Campuses'))
    except Exception as e:
        print(e)
        raise PreventUpdate


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
    Output('employee-student-health-box', 'figure'),
    Output('employee-student-health-pie', 'figure'),
    Output('employee-student-total-graph', 'figure'),
    Output('general-overview', 'children'),
    Output('general-daily-average', 'children'),
    Output('collapse-text', 'children')
], [Input('data', 'data'),
    Input('general-tabs', 'active_tab')])
def campus_graphs(data, active_tab):
    try:
        # Converting string to data frame
        df = __string_to_df(data)

        if active_tab == 'tampa':
            return tampa_tab_content(df)
        elif active_tab == 'st-pete':
            return st_pete_tab_content(df)
        elif active_tab == 'health':
            return health_tab_content(df)
    except Exception as e:
        print('Campus Graph: ', e)
        raise PreventUpdate


def tampa_tab_content(df):
    tampa = df[df['locations'] == 'Tampa']
    tampa['dates'] = tampa['dates'].apply(
        lambda date: datetime.strptime(date, '%B %d %Y'))
    employeeAvg, studentAvg = __get_daily_average(tampa)
    result, status, mostRecent, lastValue = __get_percent(tampa)
    student = tampa[tampa['occupations'] == 'Student']
    employee = tampa[tampa['occupations'] == 'Employee']

    return dict(data = gg.generate_employee_student_daily_graph(student, employee), layout = gg.stacked_graph_layout('Student Vs. Employee Daily Cases (USF Tampa)')),\
        dict(data = gg.generate_box_plot(student, employee), layout = gg.general_graph_layout('Box Plot For Daily Cases Per Occupation (USF Tampa)')),\
        dict(data = gg.generate_pie_plot(student, employee), layout = gg.general_graph_layout('Total Cases Percentage Per Occupation (USF Tampa)')),\
        dict(data = gg.generate_employee_student_total_graph(student, employee), layout = gg.general_graph_layout('Student Vs. Employee Total Cases (USF Tampa)')),\
        f'The USF Tampa campus has seen a {result:.2%} {status} in cases in the last two weeks. The number of cases went from {lastValue} to {mostRecent}.',\
        __create_avg_string(employeeAvg, studentAvg), tampa_collapse()
        
def tampa_collapse():
    return [
                html.H5('The plot represents the distribution of Covid-19 cases through their quartiles'),
                html.Ul([
                    html.Li(html.H6('The number of cases per day for an occupation is concentrated between the lower(Q1) and upper(Q3) quartiles.')),
                    html.Li(html.H6('The mean represents the average number of daily reported cases for the occupation.')),
                ]),
                html.H5('''The data suggests that students on the Tampa Campus have a higher mean and a more distributed box
                                plot. This could be due to a higher probability of students assembling in groups.''')
                ]


def st_pete_tab_content(df):
    st_pete = df[df['locations'] == 'St. Pete']
    st_pete['dates'] = st_pete['dates'].apply(
        lambda date: datetime.strptime(date, '%B %d %Y'))
    employeeAvg, studentAvg = __get_daily_average(st_pete)
    result, status, mostRecent, lastValue = __get_percent(st_pete)
    student = st_pete[st_pete['occupations'] == 'Student']
    employee = st_pete[st_pete['occupations'] == 'Employee']

    return dict(data = gg.generate_employee_student_daily_graph(student, employee), layout = gg.stacked_graph_layout('Student Vs. Employee Daily Cases (USF St. Pete)')),\
        dict(data = gg.generate_box_plot(student, employee), layout = gg.general_graph_layout('Box Plot For Daily Cases Per Occupation (USF St. Pete)')),\
        dict(data = gg.generate_pie_plot(student, employee), layout = gg.general_graph_layout('Total Cases Percentage Per Occupation (USF St. Pete)')),\
        dict(data = gg.generate_employee_student_total_graph(student, employee), layout = gg.general_graph_layout('Student Vs. Employee Total Cases (USF St. Pete)')),\
        f'The USF St. Pete campus has seen a {result:.2%} {status} in cases in the last two weeks. The number of cases went from {lastValue} to {mostRecent}.',\
        __create_avg_string(employeeAvg, studentAvg, 'St Pete'), st_pete_collapse()
        
def st_pete_collapse():
    return [
                html.H5('The plot represents the distribution of Covid-19 cases through their quartiles'),
                html.Ul([
                    html.Li(html.H6('The number of cases per day for an occupation is concentrated between the lower(Q1) and upper(Q3) quartiles.')),
                    html.Li(html.H6('The mean represents the average number of daily reported cases for the occupation.')),
                ])
                # html.H5('''The data suggests that students on the Tampa Campus have a higher mean and a more distributed box
                #                 plot. This could be due to a higher probability of students assembling in groups.''')
                ]


def health_tab_content(df):
    health = df[df['locations'] == 'Health']
    health['dates'] = health['dates'].apply(
        lambda date: datetime.strptime(date, '%B %d %Y'))
    EmployeeAvg = health['cases'].mean()
    employeeAvg, studentAvg = __get_daily_average(health)
    result, status, mostRecent, lastValue = __get_percent(health)
    student = health[health['occupations'] == 'Student']
    employee = health[health['occupations'] == 'Employee']
    return dict(data = gg.generate_employee_student_daily_graph(student, employee), layout = gg.stacked_graph_layout('Student Vs. Employee Daily Cases (USF Health)')),\
        dict(data = gg.generate_box_plot(student, employee), layout = gg.general_graph_layout('Box Plot For Daily Cases Per Occupation (USF Health)')),\
        dict(data = gg.generate_pie_plot(student, employee), layout = gg.general_graph_layout('Total Cases Percentage Per Occupation (USF Health)')),\
        dict(data = gg.generate_employee_student_total_graph(student, employee), layout = gg.general_graph_layout('Student Vs. Employee Total Cases (USF Health)')),\
        f'USF Health has seen a {result:.2%} {status} in cases in the last two weeks. The number of cases went from {lastValue} to {mostRecent}.',\
        __create_avg_string(employeeAvg, studentAvg, 'Health'), health_collapse()
        
def health_collapse():
     return [
                html.H5('The plot represents the distribution of Covid-19 cases through their quartiles'),
                html.Ul([
                    html.Li(html.H6('The number of cases per day for an occupation is concentrated between the lower(Q1) and upper(Q3) quartiles.')),
                    html.Li(html.H6('The mean represents the average number of daily reported cases for the occupation.')),
                ]),
                html.H5('''The data suggests that the employees working for USF Health have a higher mean and a more distributed box
                                plot. This could be due to a higher probability of exposure to infected patients.''')
                ]


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