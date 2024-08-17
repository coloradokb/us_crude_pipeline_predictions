import pandas as pd
from db_conn import DatabaseConnector
import logging

logger = logging.getLogger(__name__)


class PredictionData:

    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
        # self.db_file_loc = db_file_loc
        db_obj = DatabaseConnector()
        self.db_conn = db_obj.get_connection()

    def read_pipeline_pred(self, return_type='json', target_name='TOTALSUPPLY'):
        qry = f"select predictions.report_date, predictions.actual_supply, predictions.prediction,  \
              (predictions.prediction - predictions.actual_supply) as value_err, \
              ROUND(IFNULL(CAST((predictions.prediction - predictions.actual_supply) AS REAL) / NULLIF(predictions.actual_supply, 0), 0), 3) AS err_rate, \
              eia_pipelines.name from predictions left join eia_pipelines on eia_pred_target_id=eia_pipelines.id \
              where report_date >= '{self.start_date}' and report_date <= '{self.end_date}' \
              and name='{target_name}' order by report_date asc"
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(qry)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=columns)
            cursor.close()
            return df
        except Exception as e:
            logger.error(f"Data retrieval error: {e}")
            return False


# example
#while True:
#    obj = PredictionData('2023-11-09','2024-12-31','../utils/db/pipeline_predictions.db')
#    obj.read_pipeline_pred()
#    time.sleep(20)
#    print("========================================")
