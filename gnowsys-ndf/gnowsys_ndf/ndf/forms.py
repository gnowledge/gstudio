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
NODE_TYPE_CHOICES = []
ATTRIBUTE_CHOICES = {}
RELATION_CHOICES = {}


GROUP_CHOICES.append(("all","All"))
group_map = {}
gsystem_map = {}
attribute_map = {}
relation_map = {}

with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/groupmap_clix.json", 'r') as gm:
    group_map = json.load(gm)

# with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/gsystemtype_map.json") as gstm:
#     gsystem_map = json.load(gstm)


# with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/attribute_map.json") as attrm:
#     attribute_map = json.load(attrm)


# with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/gsystemtype_map.json") as rm:
#     relation_map = json.load(rm)


# for i in gsystem_map.keys():
#     tup = (gsystem_map[i],i)
#     NODE_TYPE_CHOICES.append(tup)


# for at_id in attribute_map.keys():
#     att_array = []
#     for attr in attribute_map[at_id]:
#         tup = (attr,attr)
#         att_array.append(tup)
#     ATTRIBUTE_CHOICES[at_id] = att_array

# for rt_id in relation_map.keys():
#     rt_array = []
#     for relation in relation_map[rt_id]:
#         rt_array.append(relation)
#     RELATION_CHOICES[at_id] = rt_array


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

# class AdvancedSearchForm(forms.Form):

#     query = forms.CharField(label = '', widget = forms.TextInput(attrs={'placeholder': 'Search for'}), error_messages = False)
#     ntype_choice = forms.ChoiceField(label = "Node Type", widget = forms.Select, choices = NODE_TYPE_CHOICES)
#     at_choice = {}
#     for at_id in ATTRIBUTE_CHOICES.keys():
#         at_choice[at_id] = forms.ChoiceField(label = "Attribute Type", widget = forms.Select, choices = ATTRIBUTE_CHOICES[at_id])
#     rt_choice = {}
#     for rt_id in RELATION_CHOICES.keys():
#         rt_choice[rt_id] = forms.ChoiceField(label = "Relation Type", widget = forms.Select, choices = RELATION_CHOICES[at_id])


