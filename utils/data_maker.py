import os
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
import requests
#from requests import get
from dateutil.parser import parse as parsedate

class DataMaker:
    def __init__(self, start_date, file_dir, file_name, sep_char):
        # The start date is the date we want to start our data from and drop all data before it
        self.start_date = start_date
        self.file_dir = file_dir
        self.file_name = file_name
        self.full_file_loc = file_dir + "/" + file_name
        self.sep_char = sep_char

    def check_for_file(self, file):
        if os.path.exists(file):
            return True
        else:
            return False

    def make_full_datafile(self, *files): #, sep_char, df_cols):
        """
        Takes a list of files and merges them into one dataframe
        """
        df_full = pd.DataFrame()
        i = 0
        if len(files) > 0:
            print(f"IN IF - count of files: {len(files)}")
            df = pd.DataFrame()
            for file in files:
                if self.check_for_file(file):
                    df = pd.read_csv(file, sep=",")
                    # df.dropna(inplace=True)
                    df['Date'] = pd.to_datetime(df['Date'])
                    # df.sort_values(by=['Date'], inplace=True)                    
                    df = df.rename(columns={'Date': 'ds'})
                    df = df.loc[(df['ds'] >= self.start_date)]
                    if i == 0:
                        df_full = df
                    else:
                        df_full = pd.merge(df_full, df, on='ds', how='outer')
                    i += 1
            return df_full
        else:
            return None

    def make_datafile(self, df):
        try:
            df.to_csv(self.file_dir + "/" + self.file_name, sep=self.sep_char)
            # print(f"location: {self.file_dir + '/' + self.file_name}")
            return 'Success'
        except Exception as E:
            print(f"ERROR: {E}")
            return 'fail'

# Example usage:
# obj = DataMaker('2010-01-01','data','all_eia_data.csv',',')
# full_df = obj.make_full_datafile('data/all_eia_stock_sheet_latest.csv', \
#     'data/eia_futures_latest.csv')
# print(full_df.tail(5))
# obj.make_datafile(full_df)
