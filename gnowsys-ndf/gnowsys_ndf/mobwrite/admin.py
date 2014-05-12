# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# Written 2009 by j@mailb.org

from django.contrib import admin
from reversion.admin import VersionAdmin

import models


class TextObjAdmin(VersionAdmin):
    search_fields = ['filename', 'text']
    list_display = ('filename', 'updated')
admin.site.register(models.TextObj, TextObjAdmin)

