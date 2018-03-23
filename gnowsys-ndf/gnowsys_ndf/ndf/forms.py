import datetime

from django import forms
from django_mongokit.forms import DocumentForm
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from models import Node
from models import GSystemType

from registration.forms import RegistrationForm
from passwords.fields import PasswordField

class NodeForm(DocumentForm):

    tags = forms.CharField(max_length=250)
    
    def clean_tags(self):
        value = self.cleaned_data['tags']
        return [tag.strip() for tag in value.split(',')]

    class Meta:
        document = Node
        fields = ['name', 'member_of', 'tags']
        
class UserRegistrationForm(RegistrationForm):
    password1 = PasswordField(label="Password")

class UserChangeform(PasswordChangeForm):
    new_password1 = PasswordField(label="New password") 

class UserResetform(SetPasswordForm):
    new_password1 = PasswordField(label="New password")


class mform(forms.Form):
    Username = forms.CharField(label='username', max_length=100)
    Password = forms.CharField(label='password', max_length=100,widget=forms.PasswordInput)

