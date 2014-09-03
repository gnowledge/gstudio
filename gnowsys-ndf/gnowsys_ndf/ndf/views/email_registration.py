"""Views for the registration_email app."""

from django.contrib.auth.views import password_reset
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.response import TemplateResponse


def password_reset_email(request, *args, **kwargs):
    if request.method == "POST":
        eml=request.POST.get('email',None)
        if eml:
            obju=User.objects.filter(email=eml)
            if not obju:
                return HttpResponseRedirect(reverse('password_reset_error'))
    return password_reset(request,*args,**kwargs)


def password_reset_error(request,*args,**kwargs):
    if request.method == "POST":
        eml=request.POST.get('email',None)
        if eml:
            obju=User.objects.filter(email=eml)
            print "object=",obju
            if not obju:
                return HttpResponseRedirect(reverse('password_reset_error'))
            else:
                return password_reset(request,*args,**kwargs)
    password_reset_form=PasswordResetForm
    form=password_reset_form()
    template_name="registration/password_reset_error_form.html"
    context={
        'form':form,}
    return TemplateResponse(request, template_name, context)

