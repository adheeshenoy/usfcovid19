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

app.layout = html.Div(
    [dcc.Store(id='data', data=data.__get_data()), layouts.USFLayout])


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
        df = hf.string_to_df(data)

        # Get for each location
        dfByLocation = hf.get_df_by_location(df)

        # Get total cases for each location
        totalCasesTampa, totalCasesStPete, totalCasesHealth = hf.get_total_cases_by_location(
            dfByLocation)

        # Get daily cases for each location
        dailyCasesTampa, dailyCasesStPete, dailyCasesHealth = hf.get_daily_cases_by_location(
            dfByLocation)

        data_table = hf.generate_data_table_information(df)

        return totalCasesTampa + ' cases', totalCasesHealth + ' cases',totalCasesStPete + ' cases',\
            hf.create_daily_cases_string(dailyCasesTampa), hf.create_daily_cases_string(dailyCasesHealth),\
            hf.create_daily_cases_string(dailyCasesStPete),\
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
        df = hf.string_to_df(data)
        df['dates'] = df['dates'].apply(
            lambda date: datetime.strptime(date, '%B %d %Y'))
        locationList = hf.get_daily_cases_by_location(
            hf.get_df_by_location(df))

        return dict(data = gg.generate_daily_bar_graph(locationList), layout = gg.generate_bar_layout('Daily Cases on USF Campuses', 'group')),\
            dict(data = gg.generate_total_scatter_graph(locationList), layout = gg.general_graph_layout('Total Cases on USF Campuses'))
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