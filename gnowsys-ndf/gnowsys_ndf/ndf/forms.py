import datetime
import json
from django import forms
from django_mongokit.forms import DocumentForm
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from models import Node
from models import GSystemType

from registration.forms import RegistrationForm
from passwords.fields import PasswordField

CHOICES=[("all",'All'),("Author",'Users'),("image",'Images'),("video",'Video'),("text",'Text'),("audio","Audio")]
GROUP_CHOICES=[]
GROUP_CHOICES.append(("all","All"))
group_map = {}
attribute_map = {}
ATTRIBUTE_CHOICES = [("--Select--","--Select--"),("educationaluse","Educational use"),("interactivitytype","Interactivity type"),("educationalsubject","Educational subject"),("educationallevel","Educational Level"),("source","Source"),("audience","Audience"),("educationalalignment","Educational alignment"),]

secondlevel_choices = []

with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mapping_files/groupmap.json", 'r') as gm:
    group_map = json.load(gm)

with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mapping_files/attribute_map.json") as am:
    attribute_map = json.load(am)

for i in ATTRIBUTE_CHOICES:
    if i[0] != '--Select--':
        l = []
        for val in attribute_map[i[0]]:
            tup = (val,val)
            l.append(tup)
        secondlevel_choices.append(l)

for l in group_map.keys():
    tup = (l, group_map[l])
    tup = tuple(tup)
    GROUP_CHOICES.append(tup)

class SearchForm(forms.Form):
    query = forms.CharField(label = '', widget = forms.TextInput(attrs={'placeholder': 'Search for'}), error_messages = False)
    group = forms.ChoiceField(label = "Group", widget = forms.Select, choices = GROUP_CHOICES)
    select = forms.ChoiceField(label = "Filter", widget = forms.Select, choices = CHOICES)


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