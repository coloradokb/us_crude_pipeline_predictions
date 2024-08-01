import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
import yfinance as yf
import requests

sys.path.append('../utils')
from db_conn import DatabaseConnector

from dateutil.parser import parse as parsedate


class DataGrabber:

    def __init__(self, start_date, data_dir):
        # We set this date to be the start of the data we want to use and drop all data before it
        self.start_date = start_date
        self.data_dir = data_dir
        #source of barrel reserves
        self.eia_barrels_url = 'http://ir.eia.gov/wpsr/psw09.xls'
        self.eia_outfile= f'{data_dir}/psw09.xls'
        #source of historical pricing
        self.eia_oil_price_url = 'http://www.eia.gov/dnav/pet/hist_xls/RCLC1w.xls'
        self.eia_oil_price_outfile = f'{data_dir}/RCLC1w.csv'

        self.eia_oil_futures_url = 'https://www.eia.gov/dnav/pet/xls/PET_PRI_FUT_S1_W.xls'
        self.eia_oil_futures_outfile = f'{data_dir}/futures.xls'

        # store data in db from this date forward
        self.db_inventory_start_date = '2023-11-10'

        # futures date for pricing data
        self.futures_date = None

        # Check for data directory; create if not
        # data_dir = '../data'
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)



    #def __del__(self):
    #    self.db_conn.close()


    def capture_datafiles(self, url, out):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                self.exit_message(f"DATA FILE TRY RESPONSE CODE: {response.status_code}")

            totalbits = 0
            with open(out, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        totalbits += 1024
                        f.write(chunk)
                print(f"Downloaded from {url} file = ",totalbits*1025,"KB...")
        except Exception as E:
            raise SystemExit

    def process_pipeline_file(self, make_class_df: bool = False) -> pd.DataFrame:
        self.capture_datafiles(self.eia_barrels_url, self.eia_outfile)

        # Pipeline data conversion to .csv
        df = pd.read_excel(open(self.eia_outfile, 'rb'),
                           skiprows=1,
                           sheet_name='Data 6'
                          )
        df = df.drop([0]) #remove desc
        df.rename(columns={'Sourcekey':'Date'},inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])

        # Get the last date in the dataframe as this is the most recent data
        # to help facilitate the futures prices request
        # While a return value makes more sense, gonna set it into a class
        # variable for now. I believe we'll make more use of futures data soon
        self.futures_date = df['Date'].iloc[-1].strftime('%Y-%m-%d')

        df = df.set_index('Date')
        df.index = df.index.strftime('%Y-%m-%d')


        # At some point return the df, but for now save for reuse
        if make_class_df:
            self.pipeline_data_df = df

        return df

    def generate_current_pricing_file(self, period, interval) -> pd.DataFrame:
        """
        Build the current data file (csv) from requests to yfinance
        EIA current pricing data is not available in spreadsheets.
        We will use yfinance for more frequent data calls.
        """
        current_pricing_df = self.fetch_yahoo_data("CL=F", period, interval)
        current_pricing_df.rename(columns={'Close':'CurrentClose'},inplace=True)

        return current_pricing_df

    def generate_eia_futures_data(self, period, interval) -> pd.DataFrame:
        """
        Build the futures data file (csv) from requests to yfinance
        EIA futures and now pricing data is not available in spreadsheets.
        We will use yfinance for more frequent data calls.
        """
        futures_df = self.fetch_yahoo_data("BZ=F", period, interval)
        futures_df.rename(columns={'Close':'FuturesClose'},inplace=True)

        return futures_df


    def create_complete_eia_file(self, inventory_df, pricing_df, futures_df, date_to_ds: bool = True, write_out: bool = False) -> pd.DataFrame:
        """
        Merge the pipeline data, current pricing data, and futures data
        into one complete file for the model
        """
        # Merge the DataFrames on the date column
        merged_df = pd.merge(inventory_df, pricing_df[['CurrentClose']], on='Date', how='left')
        merged_df = pd.merge(merged_df, futures_df[['FuturesClose']], on='Date', how='left')
        merged_df.fillna(0, inplace=True)
        # print(merged_df.tail(5))
        # sys.exit(0)
        merged_df['TOTALSUPPLY'] = merged_df.iloc[:, 0:-2].sum(axis=1)

        cols = list(merged_df.columns)
        cols.insert(0, cols.pop(cols.index('TOTALSUPPLY')))
        merged_df = merged_df[cols]

        if date_to_ds:
            merged_df.reset_index(inplace=True)
            merged_df = merged_df.rename(columns={'Date': 'ds'})
            print("POST DATE TO DS")
            print(merged_df.tail(5))
        if write_out:
            file_name = f"{self.data_dir}/all_eia_data.csv"
            merged_df.to_csv(file_name, sep=',', encoding='utf-8')

        return merged_df


    def fetch_yahoo_data(self, ticker, period, interval):
        df = yf.download(ticker, period=period, interval=interval)

        # Create a complete date range for the year 2023
        all_days = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

        # Reindex the DataFrame to the complete date range
        df = df.reindex(all_days)

        # Fill missing 'Close' prices using forward/backward fill method
        df['Close'] = df['Close'].ffill()
        df['Close'] = df['Close'].bfill()

        df.index = df.index.strftime('%Y-%m-%d')
        df.index.name = 'Date'
        df['Date'] = pd.to_datetime(df.index)
        return df

    def create_db_connection(self): #, db_file):
        try:
            db_obj = DatabaseConnector()
            db_conn = db_obj.get_connection()
            print(f"Connected to mysql database") #: {db_file}")
        except Exception as e:
            print(f"Error connecting to mysql database: {e}")
        return db_conn

    def update_database(self, data: pd.DataFrame) -> None:
        conn = self.create_db_connection()
        cursor = conn.cursor()
        print("tail--------")
        print(data.tail(5))
        print(data.describe())

        # We only want records post 2023-11-10 as that is when
        # we began making predictions
        new_df = data[data.index > self.db_inventory_start_date]
        print("new df_--------")
        print(new_df.tail(5))
        # Update the records in the "predictions" table
        try:
            for index, row in new_df.iterrows():
                #print(f"Index: {index.date}")
                db_index = pd.to_datetime(index).date()
                print(f"DB_INDEX: {db_index}")
                print(f"DB==>row: {row['WCESTUS1']}")
                sql = "UPDATE predictions SET actual_supply=%s, eia_pred_target_id=%s WHERE report_date=%s" # customers (id, name) VALUES (%s, %s)"
                print(f"Params: {row['WCESTUS1']}, 1, {db_index}")
                cursor.execute(sql, (row['WCESTUS1'], 1, db_index)) # "Valley 345"))
                conn.commit()
                print("Records updated successfully.")
        except Exception as e:
            print(f"Error updating records: {e}")

        conn.close()

    def process_all_files(self, make_class_df: bool = False):
        #self.capture_datafiles()
        pipeline_levels_df = self.process_pipeline_file(make_class_df)
        print(f"PIPELINE LEVELS: {pipeline_levels_df.tail(5)}")
        current_pricing_df = self.generate_current_pricing_file("10y", "1d")
        print(f"CURRENT PRICING: {current_pricing_df.tail(5)}")
        futures_df = self.generate_eia_futures_data("10y", "1d")
        print(f"FUTURES: {futures_df.tail(5)}")

        self.create_complete_eia_file(pipeline_levels_df, current_pricing_df, futures_df, date_to_ds=True, write_out=True)

    def exit_message(self, message):
        print(f"An error occurred and processing has been stopped. \n{message}")
        quit()

# Example usage:
# dg_obj = DataGrabber('2020-01-01','/tmp')
# dg_obj.fetch_yahoo_data("CL=F")
# print(dg_obj.retrieve_predictions('2023-12-15'))
# dg_obj.process_all_files()
# dg_obj.process_pipeline_file()
# dg_obj.process_eia_pricing_file()
# dg_obj.process_eia_futures_file()
