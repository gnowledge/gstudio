"""Views for the registration_email app."""

from django import forms
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import password_reset
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse

from registration_email.forms import EmailRegistrationForm

from gnowsys_ndf.ndf.views.methods import get_execution_time

attrs_dict = {'class': 'required'}

def generate_username(username):
    """
    Checks for the unique username.

    """
    try:
        User.objects.get(username=username)
        raise forms.ValidationError(_('User with same username exists. Please provide another username!'))
    except User.DoesNotExist:
        pass

    return username


class GstudioEmailRegistrationForm(EmailRegistrationForm):
    """
    Subclassing: class EmailRegistrationForm(forms.Form) from registration_email.forms file.

    Overriding django "form fields" and "def clean()"

    """

    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=256)),
        label=_("Email")
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=30)),
        label=_("Username")
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password")
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password (repeat)"))

    def clean(self):
        """
        Verifiy that the values entered into the two password fields match.
        Also checks for the username.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.

        """

        data = self.cleaned_data

        if data.get('your_name'):
            # Bot protection. The name field is not visible for human users.
            raise forms.ValidationError(_('Please enter a valid name.'))

        if not 'email' in data:
            return data

        if ('password1' in data and 'password2' in data):

            if data['password1'] != data['password2']:
                raise forms.ValidationError(
                    _("The two password fields didn't match."))

        self.cleaned_data['username'] = generate_username(data['username'])

        return self.cleaned_data


@get_execution_time
def password_reset_email(request, *args, **kwargs):
    if request.method == "POST":
        eml=request.POST.get('email',None)
        if eml:
            obju=User.objects.filter(email=eml)
            if not obju:
                return HttpResponseRedirect(reverse('password_reset_error'))
    return password_reset(request,*args,**kwargs)


@get_execution_time
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