import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import seaborn as sns
# import sqlite3
# from datetime import timedelta, datetime
from neuralprophet import NeuralProphet, set_log_level, set_random_seed
import sys
sys.path.append('../utils')
from db_conn import DatabaseConnector

class ModelMaker:

    def __init__(self, rand_seed, eia_regressor_columns,
                 pred_columns, full_data_file, epochs=500, n_lags=8,
                 n_forecasts=1, store_predictions=True):
        self.rand_seed = rand_seed
        self.eia_regressor_columns = eia_regressor_columns
        self.pred_columns = pred_columns
        self.regressor_count = len(eia_regressor_columns)
        self.epochs = epochs
        self.n_lags = n_lags
        self.n_forecasts = n_forecasts
        self.full_data_file = full_data_file
        self.log_level = "CRITICAL"
        self.data_separator = ','

    def make_df(self, datafile, sep_char, df_cols):
        """
        This function takes in a datafile and returns a dataframe with the columns specified in df_cols
        We expect the datafile to be a csv file with a header row and the columns specified in df_cols
        Neuralprophet requires the columns to be named ds (timestamp format) and y as the target variable
        """
        df = pd.read_csv(datafile, sep=sep_char)
        pipeline_df = df[df_cols]

        pipeline_df = pipeline_df.loc[(pipeline_df['ds'] >= '2015-01-01')]

        return pipeline_df

    def fit_model(self, df, pred_column, col_list): #feature_cols, lags, forecast_length):
        set_random_seed(self.rand_seed)
        set_log_level(self.log_level)

        df = df.rename(columns={pred_column: 'y'})
        # quantiles = [0.01, 0.99]

        m = NeuralProphet(
            n_changepoints=False,
            # Disable seasonality components
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            epochs=self.epochs,
            # Add the autogression
            n_lags=self.n_lags,
            n_forecasts=self.n_forecasts,
            # quantiles=quantiles,
        )
        # m.set_plotting_backend("matplotlib")

        for col in col_list:
            m.add_lagged_regressor(col)
        m.fit(df)

        return m

    def make_prediction(self, m, df, pred_column):
        if type(pred_column) == list:
            pred_column = pred_column[0]
        df = df.rename(columns={pred_column: 'y'})

        df_future = m.make_future_dataframe(df, n_historic_predictions=True,
                                            periods=1)
        #sys.exit(0)
        forecast = m.predict(df_future)

        # Rename and clean up
        forecast['+/-'] = (forecast['yhat1']-forecast['y']).round(0)
        forecast = forecast.round(0)
        forecast = forecast.fillna(0)

        forecast = forecast.drop(['trend'], axis=1)
        forecast.rename(columns={"y": "Actual", "yhat1": "Prediction"}, inplace=True)
        forecast = forecast.iloc[:,[0,1,2]]
        print(forecast[-13::])

        return forecast

    def full_prediction(self):
        i = len(self.eia_regressor_columns)
        # for cols in self.eia_regressor_columns:
        all_eia_cols = ['ds'] + self.pred_columns + self.eia_regressor_columns[0:i]
        full_df = self.make_df(self.full_data_file, self.data_separator, all_eia_cols)
        m_trained = self.fit_model(full_df, self.pred_columns[0], self.eia_regressor_columns[0:i])
        pred = self.make_prediction(m_trained, full_df, self.pred_columns[0])
        print(f"Prediction with columns: {self.eia_regressor_columns[0:i]}")
        # i = i - 1

        return pred

    def store_predictions(self, pred_df: pd.DataFrame, predictions_file: str):
        # Store the predictions in a file - unless it's null; then store to db
        # First we'll load the predictions file into a dataframe.
        # If it doesn't exist, we'll create it by outputting the pred dataframe
        if predictions_file is None:
            pred_df = pred_df.astype({"Prediction": 'int'})
            print(f"X: {pred_df[-1::]}")
            self.add_prediction(pred_df)
        else:
            try:
                #print(f"looking for--> {predictions_file}")
                all_pred_df = pd.read_csv(predictions_file, sep=',')
                all_pred_df["Date"] = pd.to_datetime(all_pred_df["Date"])
                pred_df.rename(columns={"ds": "Date"}, inplace=True)
                #print(pred_df.tail(5))
                target_date = pred_df["Date"].iloc[-1]
                print(f"Target date: {target_date}")
                # Update specific rows in df2 based on "Date" field
                #print(f'pred file location: {predictions_file}')
            except Exception as err:
                print(f"Oopsy: {err}")
                pred_df.rename(columns={"ds": "Date"}, inplace=True)
                pred_df.to_csv(predictions_file, sep=',',)

    def create_db_connection(self):
        conn = None
        try:
            #conn = sqlite3.connect(db_file)
            db_obj = DatabaseConnector()
            db_conn = db_obj.get_connection()
            print(f"Connected to mysql database") #: {db_file}")
            #print(f"Connected to SQLite database: {db_file}")
        except Exception as e:
            print(f"Error connecting to SQLite database: {e}")
        return db_conn

    def add_prediction(self, prediction_dict):
        conn = self.create_db_connection()
        #conn.set_trace_callback(print)
        # Create the cursor
        cur = conn.cursor()

        try:
            # Create the table
            # cur.execute("""CREATE TABLE IF NOT EXISTS predictions (
            #             id INTEGER PRIMARY KEY,
            #             report_date TEXT NOT NULL,
            #             actual_supply REAL NOT NULL,
            #             eia_pred_target_id INTEGER NOT NULL,
            #             prediction REAL NOT NULL,
            #             updated_date TEXT NOT NULL,
            #             regressor_count INTEGER NOT NULL)""")
            # # Commit the changes
            # conn.commit()
            # Lookup id of eia_pipeline we are predicting for
            cur.execute("SELECT id from eia_pipelines where name = %s", (self.pred_columns[0],))
            rows = cur.fetchall()
            col_id = rows[0][0] # We expect only a single value in tuple
            print(f"COL: {col_id}")
            print(type(col_id))

            print(f'PRED:{type(prediction_dict["Prediction"][-1::].to_string(index=False))}')
            pred_date = prediction_dict["ds"][-1::].to_string(index=False)
            pred_value = int(prediction_dict["Prediction"][-1::].to_string(index=False))


            # Check if the prediction already exists
            cur.execute(f"select id from predictions where report_date ='{pred_date}' and eia_pred_target_id = {col_id}")
            rows = cur.fetchall()
            if len(rows) == 0:
                cur.execute("""INSERT INTO predictions (report_date,eia_pred_target_id,
                            prediction, updated_date, regressor_count)
                            VALUES (%s, %s, %s, %s, %s)""",
                                (pred_date, col_id, pred_value, pred_date, self.regressor_count))
                conn.commit()
            else:
                print("Prediction already exists. Not updating automatically")
            conn.close()
            print(f"LR: {cur.lastrowid}")
            return cur.lastrowid
        except Exception as err:
            print("ERR")
            print(err)


#startTime = datetime.now()
# obj = ModelMaker(42, ['RCLC4', 'RCLC3', 'RCLC2'], ['WCESTUS1'], 600, 8, 1)
# obj.full_prediction()

# prediction = obj.fun_full_prediction()
# print(prediction)

# endTime = datetime.now()
# print(f"Total time for prediction: {endTime-startTime}")
