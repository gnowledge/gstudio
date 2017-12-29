import os
import datetime
from django.core.management.base import BaseCommand, CommandError
from pymongo import Connection
class Command(BaseCommand):

    def handle(self,*args,**options):
        #rotate the log when ever the maintanence script is executed 
        #os.path.getsize('/var/log/mongodb/mongod.log')
        conn = Connection()
        database = conn['admin']
        database.command({"logRotate":1})
        #Mongo log Rotated
        print "Mongo Log Rotated."

        #Rotate Registry and Recived File
        #code to create folders in /data Registry
        if not os.path.exists('/data/Registry'):
            os.mkdir('/data/Registry')

        if not os.path.exists('/data/receiveddata'):
            os.mkdir('/data/receiveddata')

        #code written with docker in consideration
        Registry_Log_path =  '/data/Registry'
        Recived_data_path   =  '/data/receiveddata'

        root_path =  os.path.abspath(os.path.dirname(os.pardir))
        tym_scan =  os.path.join(root_path, 'Last_Scan.txt') 

        if os.path.exists(tym_scan):
            file_output = open(tym_scan)
            last_scan = file_output.readline()
            index = last_scan.find(":")
            str1 = last_scan[index+1:]
            time = str1.strip("\t\n\r ")

        #get timestamp to append it to file name
        timestamp = datetime.datetime.now()
        timestamp = timestamp.isoformat()

        registry_path =  os.path.join(root_path, 'Registry.txt')
        filename  = "Registry.txt." + str(timestamp)

        receivedfile =  os.path.join(root_path, 'receivedfile')
        recv_filename  = "receivedfile." + str(timestamp)

        filename = os.path.join(Registry_Log_path,filename)
        recv_filename = os.path.join(Recived_data_path,recv_filename)


        #time = time - datetime.timedelta(minutes=5)
        #Rotate Registry File

        cmd = os.popen("cat %s|awk '$0  < \"%s\"' >  %s" % (str(registry_path),str(time),str(filename)))
        cmd.close()
        
        d = os.popen("sed -i '1,/$TIME/d' %s" % str(registry_path) )
        d.close()
        print "Registry.txt Rotated."
        #Rotate recived file information

        cmd = os.popen("cat %s|awk '$0  < \"%s\"' >  %s" % (str(receivedfile),str(time),str(recv_filename)))
        cmd.close()
        
        d = os.popen("sed -i '1,/$TIME/d' %s" % str(receivedfile) )
        d.close()
        print "Receivedfile Rotated."


        
