"""
This script will grab the data from the EIA and create the data files needed for the model.
"""

import os
from data_grabber import DataGrabber

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the utils/data directory
data_dir = os.path.join(script_dir, '..', 'utils', 'data')

dg_obj = DataGrabber('2015-01-01', data_dir)
dg_obj.process_all_files(True)
# dg_obj.insert_supply_records(dg_obj.pipeline_data_df)
dg_obj.update_database(dg_obj.pipeline_data_df)


# No longer need DataMaker. However, the following code is an example of how to use it.
# Will keep DataMaker file in repo for now.
# dm_obj = DataMaker('2010-01-01', data_dir, 'all_eia_data.csv', ',')
# full_df = dm_obj.make_full_datafile(f'{data_dir}/all_eia_stock_sheet_latest.csv',
#                                     f'{data_dir}/eia_futures_latest.csv')
