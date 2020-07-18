import pandas as pd
import ast
from datetime import datetime, timedelta
import dash_html_components as html


def get_df_by_location(df, locations=['Tampa', 'St. Pete', 'Health']):
    '''Divides a dataframe containing multiple locations based on location'''
    dfs = []
    for location in locations:
        dfs.append(df[df['locations'] == location])
    return dfs

def get_df_by_occupation(df, occupations = ['Student','Employee']):
    '''Divides a dataframe containing multiple occupations based on occupation'''
    dfs = []
    for occupation in occupations:
        dfs.append(df[df['occupations'] == occupation])
    return dfs
    


def get_total_cases_by_location(dfByLocation):
    '''Returns a list of total cases for each location'''
    totalCases = []
    for df in dfByLocation:
        totalCases.append(str(df['cases'].sum()))
    return totalCases


def get_daily_cases_by_location(dfByLocation):
    '''Returns a list of daily cases for each location'''
    dailyCases = []
    for df in dfByLocation:
        dailyCases.append(
            df.groupby('dates', sort=False, as_index=False).sum())
    return dailyCases


def create_daily_cases_string(dailyCases):
    '''Returns a string to print for daily cases'''
    text = str(dailyCases['cases'].iloc[-1]) + ' cases (' if dailyCases['cases'].iloc[-1] > 1 else\
        str(dailyCases['cases'].iloc[-1]) + ' case ('
    return text + str(dailyCases['dates'].iloc[-1]) + ')'


def generate_data_table_information(df):
    '''Returns the information needed for generating the data table'''
    return ([{'name': i, 'id': i} for i in df.columns], df.to_dict('records'))


def string_to_df(string):
    '''Helper function that converts a string into a dataframe'''
    if isinstance(string, str):
        return pd.DataFrame(ast.literal_eval(string))


def get_percent(df, days=14):
    '''Helper function that returns percentage of increase in cases in the specified
    number of days. 
    Output: result (percentage), status(increase or decrease), mostRecent value,
    Last updated value.'''
    lastTenDays = df.groupby('dates', sort=False, as_index=False).sum()
    lastTenDays['cases'] = lastTenDays['cases'].cumsum()
    lastTenDays = lastTenDays.tail(days + 1)
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


def get_daily_average(df):
    '''returns the daily average for each occupation'''
    temp = df.groupby('occupations').mean()
    return temp['cases'][0], temp['cases'][1]


def create_avg_string(employeeAvg, studentAvg, campus):
    '''returns a string that specifies the daily average for student vs employees'''
    ratio = studentAvg / employeeAvg
    return f'On average per day, {ratio:.2} times the number of students are tested positive compared to USF {campus} employees.'\
            if(ratio != 1.0) else f'On average per day, the same number of students are tested positive as USF {campus} employees.'
            
def generate_collapse(active_tab):
    '''Returns content for the collapse within the respective tabs based on the active_tab input'''
    text = [
                html.H5('The plot represents the distribution of Covid-19 cases through their quartiles'),
                html.Ul([
                    html.Li(html.H6('The number of cases per day for an occupation is concentrated between the lower(Q1) and upper(Q3) quartiles.')),
                    html.Li(html.H6('The mean represents the average number of daily reported cases for the occupation.')),
                ])]
    if active_tab == 'Tampa':
            text.append(html.H5('''The data suggests that students on the Tampa Campus have a higher mean and a more distributed box
                                plot. This could be due to a higher probability of students assembling in groups.'''))
    elif active_tab == 'St. Pete':
            #TODO ADD ANALYSIS FOR ST.PETE
            pass
    elif active_tab == 'Health':
            text.append(html.H5('''The data suggests that the employees working for USF Health have a higher mean and a more distributed box
                                plot. This could be due to a higher probability of exposure to infected patients.'''))
    return text
