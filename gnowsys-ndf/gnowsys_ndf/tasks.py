from __future__ import absolute_import
from gnowsys_ndf.celery import app
import subprocess

@app.task
def run_syncdata_script():
	script_name = 'send_syncdata'
	command = "python manage.py " + script_name
	subprocess.call([command],shell=True)
	return script_name + ' executed'
