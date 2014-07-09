"""
from django.core.management.base import BaseCommand, CommandError


file_path = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/wikidata_log.txt')

def start_writing():
	my_log = open(file_path, "w")
	my_log.write("HelloWorld!\n")
	my_log.write(":P")
	my_log.close()


class Command(BaseCommand):
        def handle(self, *args, **options):
		start_writing()
"""
import os
log_file_path = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/wikidata_log.txt')
my_log = open(log_file_path, "w")



def log_topic_created(label, log_flag):	
	"""
	Function to write message in log file when topic is created.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
	captcha = "#"
	while log_flag != 0:
		captcha += "#"
		log_flag-=1
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
	my_log.write(str(captcha) + (mylabel) + "---Topic CREATED\n")

def log_topic_exists(label, log_flag):
	"""
	Function to write message in log file if topic already exists.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = "#"
        while log_flag != 0:
                captcha += "#"
                log_flag-=1
        mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
	my_log.write(str(captcha) + unicode(mylabel) + "---Topic EXISTS\n")

def log_attributeType_created(label, log_flag):
	"""
	Function to write message in log file when attributeType is created.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
	captcha += "-"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---AttributeType CREATED\n")

def log_attributeType_exists(label, log_flag):
	"""
	Function to write message in log file if attributeType already exists.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""

        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
	captcha += "-"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---AttributeType EXISTS\n")

def log_attribute_created(label, log_flag):
    	"""
	Function to write message in log file when attribute is created.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""  
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "@"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Attribute CREATED\n")

def log_attribute_exists(label, log_flag):
	"""
	Function to write message in log file if attribute already exists.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "@"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Attribute EXISTS\n")


def log_relationType_created(label, log_flag):
	"""
	Function to write message in log file when relationType is created.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "$"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---RelationType CREATED\n")

def log_relationType_exists(label, log_flag):
	"""
	Function to write message in log file if relationType already exists.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "$"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---RelationType EXISTS\n")

def log_relation_created(label, log_flag):
	"""
	Function to write message in log file when relation is created.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "*"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Relation CREATED\n")

def log_relation_exists(label, log_flag):
	"""
	Function to write message in log file if relation already exists.
	Parameters being passed -
	1)label- name of the item
	2)log_flag - controls indentation to make the log file readable

	"""
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "*"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Relation EXISTS\n")


def log_inner_topic_start(log_flag):
	"""
	Helper log function that print messages to help in debugging

	"""
        captcha = "-"
        my_log.write("\n")
        while log_flag != 0:
                captcha += "-"
                log_flag-=1
        my_log.write(str(captcha) + "-----------------------------------------------------------------------\n")

def log_inner_topic_end(log_flag):
	"""
	Helper log function that print messages to help in debugging

	"""
        captcha = "-"
        my_log.write("\n")
        while log_flag != 0:
                captcha += "-"
                log_flag-=1
        my_log.write(str(captcha) + "_______________________________________________________________________\n")



def log_outer_topic(log_flag):
	"""
	Helper log function that print messages to help in debugging

	"""
        captcha = "-"
        my_log.write("\n")
        while log_flag != 0:
                captcha += "-"
                log_flag-=1
        my_log.write(str(captcha) + "-----------------------------------------------------------------------\n")
	my_log.write(str(captcha) + "-----------------------------------------------------------------------\n")
