# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# Written 2009 by j@mailb.org

from django.contrib import admin #importing admin module
from reversion.admin import VersionAdmin 

import models #importing all the things from model.py


class TextObjAdmin(VersionAdmin):
    search_fields = ['filename', 'text']
    list_display = ('filename', 'updated')
admin.site.register(models.TextObj, TextObjAdmin) #register id used so that it is aware of admin class

