import os
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
# obj = ModelMaker(42, ['WCESTP11','WCESTP21','W_EPC0_SAX_YCUOK_MBBL',
#                       'WCESTP31','WCESTP41','WCESTP51','W_EPC0_SKA_NUS_MBBL','WCSSTUS1',
#                       'WGTSTUS1','WGTSTP11','WGTSTP21','CurrentClose','FuturesClose'], ['WCESTUS1'], csv_file_path, 3000, 8, 1)


## Create TOTALSUPPLY prediction and store into db
# The end value in ModelMaker is the index of the eia_pipelines table
# that is a fk to the predictions table. For now we'll do 2 passes.
# One for TOTALSUPPLY and then for WCESTUS1
regressor_columns = regressor_cols.feature_selection()
regressor_columns.remove('TOTALSUPPLY')
obj = ModelMaker(42, regressor_columns, ['TOTALSUPPLY'], csv_file_path, 3000, 8, 1)
prediction = obj.full_prediction()
obj.store_predictions(prediction, pred_file_path)

regressor_columns = regressor_cols.feature_selection()
regressor_columns.remove('WCESTUS1')
obj = ModelMaker(42, regressor_columns, ['WCESTUS1'], csv_file_path, 3000, 8, 1)
prediction = obj.full_prediction()
obj.store_predictions(prediction, pred_file_path)


endTime = datetime.now()
print(f"Total time for prediction: {endTime-startTime}")
