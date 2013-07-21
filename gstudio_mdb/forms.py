from django.forms import ModelForm
from gstudio_mdb.models import Comment
from gstudio_mdb.models import Relation


class CommentForm(ModelForm):

    def __init__(self, object, *args, **kwargs):
        """Override the default to store the original document
        that comments are embedded in.
        """
        self.object = object
        return super(CommentForm, self).__init__(*args, **kwargs)

    def save(self, *args):
        """Append to the comments list and save the node"""
        self.object.comments.append(self.instance)
        self.object.save()
        return self.object

    class Meta:
        model = Comment

class RelationForm(ModelForm):

    def __init__(self, object, *args, **kwargs):
        """Override the default to store the relations as embedded
        list.
        """
        self.object = object
        return super(RelationForm, self).__init__(*args, **kwargs)

    def save(self, *args):
        """Append to the relations list and save the node"""
        self.object.relations.append(self.instance)
        self.object.save()
        return self.object

    class Meta:
        model = Relation
