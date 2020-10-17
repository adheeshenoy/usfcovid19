from apscheduler.schedulers.blocking import BlockingScheduler
import helper_functions as hf
import pandas as pd
from app import db
from data import __get_data
from datetime import datetime
from tzlocal import get_localzone

sched = BlockingScheduler(timezone=get_localzone())

class Predictions(db.Model):
    '''Defines a table for the database and the data types for its columns'''
    __tablename__ = 'prediction'

    DS = db.Column(db.Text(40), nullable=False, primary_key=True)
    YHAT_TAMPA = db.Column(db.Text(40), nullable=False)
    YHAT_ST_PETE = db.Column(db.Text(40), nullable=False)
    YHAT_HEALTH = db.Column(db.Text(40), nullable=False)
    # YHAT_SARASOTA = db.Column(db.Text(40), nullable=False)

    # YHAT_SARASOTA
    def __init__(self, DS, YHAT_TAMPA, YHAT_ST_PETE, YHAT_HEALTH):
        self.DS = DS
        self.YHAT_TAMPA = YHAT_TAMPA
        self.YHAT_ST_PETE = YHAT_ST_PETE
        self.YHAT_HEALTH = YHAT_HEALTH
        # self.YHAT_SARASOTA = YHAT_SARASOTA
    
#TODO Add covid data to database    
# class covid_data(db.Model):
#     '''Defines a table for the database and the data types for its columns'''
#     __tablename__ = 'covid_data'

#     dates = db.Column(db.Text(40), nullable=False, primary_key=True)
#     locations = db.Column(db.Text(40), nullable=False)
#     occupations = db.Column(db.Text(40), nullable=False)
#     cases = db.Column(db.Text(40), nullable=False)

#     def __init__(self,dates, locations, occupations, cases):
#         self.dates = dates
#         self.locations = locations
#         self.occupations = occupations
#         self.cases = cases

@sched.scheduled_job('interval', weeks = 4)
def get_predictions():
    '''Function that runs once a week to calculte new predictions on the current data and stores the predictions on a Postgres DB.'''

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print('UPDATING PREDICTION DATA ' + str(datetime.today()) + ' AT ' + str(current_time) + "\n\n\n")
    df = __get_data()
    location_list = hf.get_df_by_location(df)
    location_list = hf.format_dfs_for_prediction(location_list)
    tampa_prediction = hf.get_prediction(location_list[0])
    st_pete_prediction = hf.get_prediction(location_list[1])
    health_prediction = hf.get_prediction(location_list[2])
    # sarasota_prediction = hf.get_prediction(location_list[3])

    new_df = pd.merge(tampa_prediction, st_pete_prediction, on=['ds'])
    new_df = pd.merge(new_df, health_prediction, on=['ds'])
    # new_df = pd.merge(new_df, sarasota_prediction, on=['ds'])
    new_df = new_df.rename(
        columns={'ds': 'DS', 'yhat_x': 'YHAT_TAMPA', 'yhat_y': 'YHAT_ST_PETE', 'yhat': 'YHAT_HEALTH'})
    new_df.to_sql('prediction', con=db.engine, if_exists='replace', index=False)

sched.start()
