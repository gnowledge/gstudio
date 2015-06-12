from gnowsys_ndf.ndf.models import *
from django.http import HttpResponse
import random
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from datetime import date,time,timedelta
import json
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
 bench_cur = col.find({'last_update':{'$gte':Today}}).sort('last_update', -1)
 
 search_cur = []
 if request.method == "POST":
      if request.POST.get('searchmethod','') != '':
          search_cur = col.find({'name':unicode(request.POST.get('searchmethod',''))}).sort('last_update', -1).sort('time_taken',-1)
          
      else:
        if request.POST.get('methodlist','') != "ALL":
          print "sadfasfasdf",request.POST.get('methodlist','')
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
         avg = 0
         a = new_list.pop()
         a.update({'avg':total})
         new_list.append(a)
    avg = float (i['time_taken']) +avg
    count = count + 1
    last_name = i['name']
    new_list.append(i)
 if new_list:
    a = new_list.pop()   
    a.update({'avg':(avg/count)})
    new_list.append(a)
 bench_cur.rewind()          
 return render_to_response("reports.html",
                           {'bench_cur':new_list,
                            'listofmethods':listofmethods,
                            'search_cur':search_cur 
                           
                           },context_instance = RequestContext(request)) 


def month_view(request):
 periodicview = request.POST.get('periodview','')
 
 if periodicview == 'day':
    timedelta1 = 0
 if periodicview == 'week':
    timedelta1 = 7
 if periodicview == 'month':
    timedelta1 = 30
 if not periodicview:
   timedelta1= 0   
 date1=datetime.date.today() - timedelta(timedelta1) 
 ti=time(0,0)
 listofmethods = []
 Today=datetime.datetime.combine(date1,ti)
 
 bench_cur = col.aggregate([{'$match':{'last_update':{'$gte':Today}}}, {
       '$group':
         {
           '_id': "$name",
           'time_taken': { '$sum': 1 },
         }
         
     },{'$sort': { 'time_taken': -1 }}
   ]
   
   )
                                  
     #write a code to check to find the frequency of the most executed method
     #primarily focus on the method getting maximum number of hits
 return render_to_response("frequency_reports.html",
                           {'bench_cur':json.dumps(bench_cur['result'], cls=NodeJSONEncoder),
                           },context_instance = RequestContext(request)) 
