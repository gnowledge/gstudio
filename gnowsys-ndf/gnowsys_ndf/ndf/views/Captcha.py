from django.views.generic.edit import CreateView
import json
from django import forms
from captcha.fields import CaptchaField
from django.http import HttpResponse
from django.http import StreamingHttpResponse

class CaptchaTestForm(forms.Form):
    ''' class to instantiate CaptchaField() '''    
    captcha = CaptchaField()

def captcha_validate(request):
    valid = ""
    data = request.POST.getlist('formData[]','')
    data = convert_list_dict(data)
    form = CaptchaTestForm(data)
    if form.is_valid():
            valid = True
    else:
            valid = False
    return HttpResponse(valid)

def new_captcha(request):
   ''' method to return form'''
   form = CaptchaTestForm()  
   return StreamingHttpResponse(str(form))   
   

def convert_list_dict(data):
    data_dict = {} 
    for i in data:
        new_data = i.split(':')
        data_dict.update({new_data[0]:str(new_data[1])})
    return data_dict 


