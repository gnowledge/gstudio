import datetime

from django import forms

from django_mongokit.forms import DocumentForm
from models import Node

from models import GSystemType


class NodeForm(DocumentForm):

    tags = forms.CharField(max_length=250)
    
    def clean_tags(self):
        value = self.cleaned_data['tags']
        return [tag.strip() for tag in value.split(',')]

    class Meta:
        document = Node
        fields = ['name', 'member_of', 'tags']
        

