# Description: This file contains the FastAPI code to create an API endpoint that returns the pipeline level predictions.
import time
import json
from fastapi import FastAPI, Response
from prediction_data import PredictionData
from typing import Optional
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = FastAPI()


# Define a Pydantic model
class PredAPIModel(BaseModel):
    prediction: str


# Example function to validate input
def validate_input(value):
    try:
        # Create an instance of the model with the provided value
        model_instance = PredAPIModel(prediction=value)
        logger.info("Prediction paramter validation successful: %s", 
                    model_instance.prediction)
    except ValidationError as e:
        # Handle validation errors
        logger.info("Prediction paramter validation error: %s",
                    e)


@app.get('/predictions')
def get_data(target: Optional[str] = 'TOTALSUPPLY'):
    validate_input(target)

    obj = PredictionData('2023-11-09', '2031-12-31')
    pred_data_df = obj.read_pipeline_pred('json', target)
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
