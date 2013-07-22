from django.db import models


from django.db import models
from django.core.urlresolvers import reverse

from djangotoolbox.fields import ListField, EmbeddedModelField


class Node(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    comments = ListField(EmbeddedModelField('Comment'), editable=False)
    relations = ListField(EmbeddedModelField('Relation'), editable=False)
    author = models.CharField(verbose_name="Author's Name", max_length=255)


    def get_absolute_url(self):
        return reverse('node', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField(verbose_name="Comment")
    author = models.CharField(verbose_name="Name", max_length=255)

class Relation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = ListField(EmbeddedModelField('RelationType'), editable=False)
    pobject = ListField(EmbeddedModelField('Node'), editable=False)
    author = models.CharField(verbose_name="Name", max_length=255)

class RelationType(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(verbose_name="Name", max_length=255)
    inverseName = models.CharField(verbose_name="Name", max_length=255)
    author = models.CharField(verbose_name="Name", max_length=255)
    slug = models.SlugField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('relationtype', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
