import sys
import os
from sklearn.feature_selection import SelectKBest, f_regression
from model_predictor import ModelMaker
import regressor_cols


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the utils/data directory
data_dir = os.path.join(script_dir, '..', 'utils', 'data')
csv_file_path = os.path.join(data_dir, 'all_eia_data.csv')

column_list = regressor_cols.feature_selection()
obj = ModelMaker(42, column_list, ['TOTALSUM'], csv_file_path, 300, 8, 1)
df = obj.make_df(csv_file_path, ',', column_list)
# Assuming df is your DataFrame
# Fill empty values with 0
df.fillna(0, inplace=True)

# Feature selection to find the top k features
X = df.drop(columns=['ds', 'TOTALSUM'])
y = df['TOTALSUM']
selector = SelectKBest(score_func=f_regression, k=5)  # Select top 5 features
selector.fit(X, y)
selected_features = X.columns[selector.get_support()]

sys.exit(0)
# Initialize NeuralProphet model
model = NeuralProphet()

# Add selected columns as regressors
for column_list in selected_features:
    model.add_future_regressor(column_list)

# Prepare data
df_train = df[['ds', 'TOTALSUM'] + list(selected_features)]

# Fit the model
model.fit(df_train, freq='D')

# Make predictions
future = model.make_future_dataframe(df, periods=30, n_historic_predictions=len(df))
forecast = model.predict(future)

# Display the forecast
print(forecast[['ds', 'yhat1', 'TOTALSUM']])
