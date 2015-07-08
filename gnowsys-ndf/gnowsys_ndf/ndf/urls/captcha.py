from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import Captcha

urlpatterns = patterns('gnowsys_ndf.ndf.views.Captcha',                        
    url(r'^validate_captcha/', 'captcha_validate', name='captcha_validate'),
    url(r'^new_captcha/', 'new_captcha', name='new_captcha')  
    )


