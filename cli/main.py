import os
import sys
from model_predictor import ModelMaker
import regressor_cols
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

pred_file_path = None

startTime = datetime.now()
regressor_columns = regressor_cols.feature_selection()
regressor_columns.sort()
looper_columns = regressor_columns.copy()

# we set these in the done list so as not to predict on them
prediction_skip_list = ["CurrentClose", "FuturesClose"]

k = 0
#for name in regressor_columns:
for i, name in enumerate(looper_columns):
    if name not in prediction_skip_list:

        print(f"Making preds for: {name}")
        regressor_columns.remove(name)
        obj = ModelMaker(42, regressor_columns, [name], csv_file_path, 3000, 8, 1)
        prediction = obj.full_prediction()
        regressor_columns.append(name)
        k = k + 1
        obj.store_predictions(prediction, pred_file_path)

endTime = datetime.now()
print(f"Total time for prediction: {endTime-startTime}")
