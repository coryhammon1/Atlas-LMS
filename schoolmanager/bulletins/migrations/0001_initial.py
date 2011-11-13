
from south.db import db
from django.db import models
from bulletins.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'BulletinComment'
        db.create_table('bulletins_bulletincomment', (
            ('id', orm['bulletins.BulletinComment:id']),
            ('bulletin', orm['bulletins.BulletinComment:bulletin']),
            ('user', orm['bulletins.BulletinComment:user']),
            ('text', orm['bulletins.BulletinComment:text']),
            ('date', orm['bulletins.BulletinComment:date']),
        ))
        db.send_create_signal('bulletins', ['BulletinComment'])
        
        # Adding model 'Bulletin'
        db.create_table('bulletins_bulletin', (
            ('id', orm['bulletins.Bulletin:id']),
            ('board', orm['bulletins.Bulletin:board']),
            ('user', orm['bulletins.Bulletin:user']),
            ('title', orm['bulletins.Bulletin:title']),
            ('text', orm['bulletins.Bulletin:text']),
            ('date', orm['bulletins.Bulletin:date']),
        ))
        db.send_create_signal('bulletins', ['Bulletin'])
        
        # Adding model 'BulletinBoard'
        db.create_table('bulletins_bulletinboard', (
            ('id', orm['bulletins.BulletinBoard:id']),
        ))
        db.send_create_signal('bulletins', ['BulletinBoard'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'BulletinComment'
        db.delete_table('bulletins_bulletincomment')
        
        # Deleting model 'Bulletin'
        db.delete_table('bulletins_bulletin')
        
        # Deleting model 'BulletinBoard'
        db.delete_table('bulletins_bulletinboard')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bulletins.bulletin': {
            'board': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bulletins'", 'to': "orm['bulletins.BulletinBoard']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'bulletins.bulletinboard': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'bulletins.bulletincomment': {
            'bulletin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['bulletins.Bulletin']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['bulletins']
