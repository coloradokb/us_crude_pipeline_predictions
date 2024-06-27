# Description: This file contains the FastAPI code to create an API endpoint that returns the pipeline level predictions.
import time
import json
from fastapi import FastAPI, Response
from prediction_data import PredictionData

app = FastAPI()

@app.get('/predictions')
def get_data():
    # Convert DataFrame to JSON
    obj = PredictionData('2023-11-09','2024-12-31','./pipeline_predictions.db')
    pred_data_df = obj.read_pipeline_pred()
    json_output = pred_data_df.to_json(orient='records')

    # Parse JSON string into list of dictionaries
    data = json.loads(json_output)

    # Add report_date_formatted field to each dictionary
    for item in data:
        report_date_timestamp = item["report_date"] / 1000  # Convert milliseconds to seconds
        formatted_date = time.strftime("%m-%d-%Y", time.localtime(report_date_timestamp))
        item["report_date_formatted"] = formatted_date

    updated_data_str = json.dumps(data)
    return Response(content=updated_data_str, media_type='application/json')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

