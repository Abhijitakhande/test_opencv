import os
import sys
import time
import logging
import servicemanager
import win32event
import win32service
import win32serviceutil
import psycopg2
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MyPythonService"
    _svc_display_name_ = "My Python Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()

    def _getLogger(self):
        logger = logging.getLogger(self._svc_name_)
        logger.setLevel(logging.DEBUG)
        log_file = os.path.join(os.path.dirname(__file__), f"{self._svc_name_}.txt")  # Change to .txt
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.logger.info("Service is starting.")
        self.main()

    def main(self):
        try:
            while True:
               # self.logger.info("Service is running...")
                self.do_task()
                time.sleep(60)  # Wait for 1 minute
                if win32event.WaitForSingleObject(self.hWaitStop, 0) == win32event.WAIT_OBJECT_0:
                    self.logger.info("Service is stopping.")
                    break
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")

    def do_task(self):
        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(
                dbname="atcpl",
                user="postgres",
                password="system",
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # Read data from source table
            cur.execute("SELECT * FROM inward ORDER BY inward_id ASC")
            rows = cur.fetchall()

         
            # Convert data to DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

            # Convert datetime columns to timezone naive
            for col in df.columns:
                if is_datetime(df[col]):
                    df[col] = df[col].dt.tz_localize(None)
                    
            df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
            # Close cursor and connection
            cur.close()
            conn.close()

            # Export DataFrame to Excel
            excel_file = os.path.join(os.path.dirname(__file__), f"{self._svc_name_}_data.xlsx")
            df.to_excel(excel_file, index=False)

            self.logger.info("Data exported to Excel successfully.")
        except Exception as e:
            self.logger.error(f"An error occurred while executing do_task(): {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)
