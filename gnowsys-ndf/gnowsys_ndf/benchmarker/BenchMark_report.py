from gnowsys_ndf.ndf.models import *
from django.http import HttpResponse
import random
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from datetime import date,time,timedelta
'''
    The First method to get called.
'''
db = get_database()  
col = db[Benchmark.collection_name]
 
def report(request):
 date1=datetime.date.today()
 ti=time(0,0)
 listofmethods = []
 Today=datetime.datetime.combine(date1,ti)
 bench_cur = col.find({'last_update':{'$gte':Today}}).sort('last_update', -1).sort('time_taken',-1)
 
 search_cur = []
 if request.method == "POST":
      if request.POST.get('methodlist','') != "ALL":
        search_cur = col.find({'name':unicode(request.POST.get('methodlist',''))}).sort('last_update', -1).sort('time_taken',-1)
             
 avg = 0                      
 count = 0
 last_name = ""
 total = 0
 loop = 0
 new_list =[]            
 for i in bench_cur:
    loop = loop  + 1 
    if i['name'] not in listofmethods:
           listofmethods.append(i['name'])
    if last_name != "" :
      if last_name != i['name']:
         total = avg/count
         count = 0
         print "asdf",loop -1 ,int(loop) - 1
         new_list[2].update({'avg':total})
         
    avg = float (i['time_taken']) +avg
    count = count + 1
    last_name = i['name']
    new_list.append(i)
    
 bench_cur.rewind()          
 return render_to_response("reports.html",
                           {'bench_cur':new_list,
                            'listofmethods':listofmethods,
                            'search_cur':search_cur 
                           
                           },context_instance = RequestContext(request)) 

