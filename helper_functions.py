import pandas as pd
import ast
from datetime import datetime, timedelta
import dash_html_components as html
from dateutil.relativedelta import relativedelta
import re
from fbprophet import Prophet
import constants as const


def get_df_by_location(df, locations=['Tampa', 'St. Pete', 'Health']):
    '''Divides a dataframe containing multiple locations based on location'''
    return [df[df['locations'] == location] for location in locations]

def get_df_by_occupation(df, occupations = ['Student','Employee']):
    '''Divides a dataframe containing multiple occupations based on occupation'''
    return [df[df['occupations'] == occupation] for occupation in occupations]
    


def get_total_cases_by_location(dfByLocation):
    '''Returns a list of total cases for each location'''
    return [str(df['cases'].sum()) for df in dfByLocation]


def get_daily_cases_by_location(dfByLocation):
    '''Returns a list of daily cases for each location'''
    return [
        df.groupby('dates', sort=False, as_index=False).sum()
        for df in dfByLocation
    ]


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





def add_range_selector(layout, axis_name='xaxis', ranges=None, default=None):    
    '''Add a rangeselector to the layout if it doesn't already have one.
    Based on https://github.com/danio/plotly_tools/blob/master/range.py
    '''
    axis = layout.setdefault(axis_name, dict())
    axis.setdefault('type', 'date')
    if ranges is None:
        # Make some nice defaults
        ranges = ['15d','1m', 'all']
    re_split = re.compile('(\d+)')
    def range_split(range):
        split = re.split(re_split, range)
        assert len(split) == 3
        return (int(split[1]), split[2])
    step_map = dict(d='day', m='month', y='year')
    def make_button(range):
        label = range
        if label == '15d':
            label = '15 Days'
        elif label == '1m':
            label = '1 Month'
        elif label == 'all':
            label = 'All'
        
        
        if range == 'all':
            return dict(step='all', label = label)
        else:
            (count, step) = range_split(range)
            step = step_map.get(step, step)
            return dict(count=count,
                label=label,
                step=step,
                stepmode='backward')
    axis.setdefault('rangeselector', dict(buttons=[make_button(r) for r in ranges]))
    if default is not None and default != 'all':
        end_date = datetime.today()
        (count, step) = range_split(default)
        step = step_map[step] + 's'
        start_date = (end_date - relativedelta(**{step: count}))
        axis.setdefault('range', [start_date, end_date])
        
        
        
        
def format_dfs_for_prediction(locationList):
    dfs = []
    for df in locationList:
        df = df.groupby('dates', sort=False, as_index=False).sum()
        df['cases'] = df['cases'].cumsum()
        df['dates'] = df['dates'].apply(lambda date: datetime.strftime(datetime.strptime(date, '%B %d %Y'), '%Y-%m-%d'))
        r = pd.date_range(start=df.dates.min(), end=df.dates.max())
        df = df.set_index('dates')
        df.index = pd.DatetimeIndex(df.index)
        df = df.reindex(r).reset_index().fillna(method = 'ffill')
        df['cases'] = df['cases'].astype(int)
        df = df.rename(columns = {'index': 'ds', 'cases':'y'})
        dfs.append(df)  
    return dfs

def get_prediction(df):
    '''Returns a data frame containing a prediction of the # of cases in the specified future period of time'''
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=50)
    forecast = m.predict(future)
    forecast['yhat'] = forecast['yhat'].apply(lambda x: int(x))
    return forecast[['ds', 'yhat']]

def get_prediction_by_location(prediction_df):
    '''Returns a list of prediction data frames based on locations.'''
    prediction_df = prediction_df.reset_index()
    return [
        prediction_df[['DS', col_name]]
        for col_name in const.PREDICTION_COL_NAMES
    ]