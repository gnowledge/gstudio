
from south.db import db
from django.db import models
from gnowsys_ndf.mobwrite.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'TextObj'
        db.create_table('mobwrite_textobj', (
            ('id', orm['mobwrite.TextObj:id']),
            ('created', orm['mobwrite.TextObj:created']),
            ('updated', orm['mobwrite.TextObj:updated']),
            ('filename', orm['mobwrite.TextObj:filename']),
            ('text', orm['mobwrite.TextObj:text']),
            ('lasttime', orm['mobwrite.TextObj:lasttime']),
        ))
        db.send_create_signal('mobwrite', ['TextObj'])
        
        # Adding model 'ViewObj'
        db.create_table('mobwrite_viewobj', (
            ('id', orm['mobwrite.ViewObj:id']),
            ('username', orm['mobwrite.ViewObj:username']),
            ('filename', orm['mobwrite.ViewObj:filename']),
            ('shadow', orm['mobwrite.ViewObj:shadow']),
            ('backup_shadow', orm['mobwrite.ViewObj:backup_shadow']),
            ('shadow_client_version', orm['mobwrite.ViewObj:shadow_client_version']),
            ('shadow_server_version', orm['mobwrite.ViewObj:shadow_server_version']),
            ('backup_shadow_server_version', orm['mobwrite.ViewObj:backup_shadow_server_version']),
            ('edit_stack', orm['mobwrite.ViewObj:edit_stack']),
            ('lasttime', orm['mobwrite.ViewObj:lasttime']),
            ('textobj', orm['mobwrite.ViewObj:textobj']),
        ))
        db.send_create_signal('mobwrite', ['ViewObj'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'TextObj'
        db.delete_table('mobwrite_textobj')
        
        # Deleting model 'ViewObj'
        db.delete_table('mobwrite_viewobj')
        
    
    
    models = {
        'mobwrite.textobj': {
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lasttime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "'You can edit this text'"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'mobwrite.viewobj': {
            'backup_shadow': ('django.db.models.fields.TextField', [], {}),
            'backup_shadow_server_version': ('django.db.models.fields.IntegerField', [], {}),
            'edit_stack': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lasttime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'shadow': ('django.db.models.fields.TextField', [], {}),
            'shadow_client_version': ('django.db.models.fields.IntegerField', [], {}),
            'shadow_server_version': ('django.db.models.fields.IntegerField', [], {}),
            'textobj': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'viewobj'", 'null': 'True', 'to': "orm['mobwrite.TextObj']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }
    
    complete_apps = ['mobwrite']
