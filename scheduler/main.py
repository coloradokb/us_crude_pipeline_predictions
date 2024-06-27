import threading
import time
import sys

sys.path.append('../utils/')

from data_grabber import DataGrabber
from data_maker import DataMaker

class ThreadManager:
    def __init__(self):
        self.thread1 = threading.Thread(target=self.function1)
        #self.thread2 = threading.Thread(target=self.function2)
        self.is_running = True

    def function1(self):
        try:
            while self.is_running:
                data_dir='/tmp/'
                print("Function 1 is running")
                dg_obj = DataGrabber('2010-01-01', '/tmp/')
                dg_obj.process_all_files(True)
                dg_obj.update_database(dg_obj.pipeline_data_df)

                dm_obj = DataMaker('2010-01-01', data_dir, 'all_eia_data.csv', ',')
                full_df = dm_obj.make_full_datafile(f'{data_dir}/all_eia_stock_sheet_latest.csv',
                                                    f'{data_dir}/eia_futures_latest.csv')
                
                full_data_file_result = dm_obj.make_datafile(full_df)
                print(full_data_file_result)
                time.sleep(5)
        except Exception as e:
            print("An error occurred in function1:", e)

    def function2(self):
        while True:
            print("Function 2 is running-10 seconds")
            time.sleep(10)

    def start_threads(self):
        self.thread1.start()
        #self.thread2.start()

    def join_threads(self):
        self.thread1.join()
        #self.thread2.join()

if __name__ == "__main__":
    while True:
        try:
            manager = ThreadManager()
            manager.start_threads()
            time.sleep(60)  # Run for 60 seconds
            manager.is_running = False  # Stop the threads
            manager.join_threads()
            print("ThreadManager completed execution. Restarting in 10 seconds...")
            time.sleep(10)  # Restart after 10 seconds
        except Exception as e:
            print("An error occurred in the main loop:", e)
