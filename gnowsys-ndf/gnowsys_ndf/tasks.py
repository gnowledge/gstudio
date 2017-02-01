# from __future__ import absolute_import
# from gnowsys_ndf.celery import app
# import subprocess
# import os
# @app.task
# def run_syncdata_script():
#     #check if last scan file is update
#     #if not skip the execution the script might be running
#     #or stuck
#     #manage directory path

#     data_fetch_script_name = 'fetch_data'
#     command = "python manage.py " + data_fetch_script_name
#     subprocess.call([command],shell=True)
#     print data_fetch_script_name + ' executed.'

#     syncdata_sending_script_name = 'send_syncdata'
#     command1 = "python manage.py " + syncdata_sending_script_name
#     subprocess.call([command1],shell=True)
#     print syncdata_sending_script_name + ' executed.'

#     syncdata_fetching_script_name = 'fetch_syncdata'
#     command2 = "python manage.py " + syncdata_fetching_script_name
#     subprocess.call([command2],shell=True)
#     print syncdata_fetching_script_name + ' executed.'

#     return 'Both scripts executed'
