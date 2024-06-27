import os
from model_predictor import ModelMaker
from datetime import timedelta, datetime

"""
This script will Run the model prediction. The expectation is the data utils
have been run and the data is updated.
"""

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the utils/data directory
data_dir = os.path.join(script_dir, '..', 'utils', 'data')
csv_file_path = os.path.join(data_dir, 'all_eia_data.csv')
# pred_file_path = os.path.join(data_dir, 'predictions.csv')
pred_file_path = None

startTime = datetime.now()
obj = ModelMaker(42, ['WCESTP11','WCESTP21','W_EPC0_SAX_YCUOK_MBBL',
                      'WCESTP31','WCESTP41','WCESTP51','W_EPC0_SKA_NUS_MBBL','WCSSTUS1',
                      'WGTSTUS1','WGTSTP11','WGTSTP21','CurrentClose','FuturesClose'], ['WCESTUS1'], csv_file_path, 3000, 8, 1)
# obj.make_df(csv_file_path, ',', ['ds', 'RCLC4', 'RCLC3', 'RCLC2', 'WCESTUS1'])
prediction = obj.full_prediction() # Predictions are printed within the method for now
#print(prediction)

obj.store_predictions(prediction, pred_file_path)

endTime = datetime.now()
print(f"Total time for prediction: {endTime-startTime}")
