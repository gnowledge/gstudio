from django.core.management.base import BaseCommand, CommandError
import os
from subprocess import call
from django.core.mail import EmailMessage

class Command(BaseCommand):
	help = 'Will call the script to generate public, private key pair. Please ensure you have edited ../gstudio/key_test/gen_key_inp.txt before running this script'

	def handle(self, *args, **kwargs):
		path0 = os.path.dirname(__file__).split('/gstudio')[0] + '/gstudio/key_script/'

		script_name = 'gen_key_script.sh'
		script_input_file_name = 'gen_key_inp.txt'

		path1 = path0 + script_name
		path2 = path0 + script_input_file_name

		# pass path2 as argument to be used by script
		# need to pass path of gen_key_input.txt to the gen_key_script.sh so that it can read it because the bash
		# command will be run from /gnowsys-ndf as:
		# $ python manage.py generate_keys 

		command = 'bash'+ ' ' + path1 + ' ' + path2
		print "command",command
		call([command],shell=True)
