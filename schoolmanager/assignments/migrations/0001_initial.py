
from south.db import db
from django.db import models
from assignments.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'AssignmentFileSubmission'
        db.create_table('assignments_assignmentfilesubmission', (
            ('id', orm['assignments.AssignmentFileSubmission:id']),
            ('assignment_submission', orm['assignments.AssignmentFileSubmission:assignment_submission']),
            ('file', orm['assignments.AssignmentFileSubmission:file']),
        ))
        db.send_create_signal('assignments', ['AssignmentFileSubmission'])
        
        # Adding model 'AssignmentGroup'
        db.create_table('assignments_assignmentgroup', (
            ('id', orm['assignments.AssignmentGroup:id']),
            ('course', orm['assignments.AssignmentGroup:course']),
            ('name', orm['assignments.AssignmentGroup:name']),
            ('weight', orm['assignments.AssignmentGroup:weight']),
        ))
        db.send_create_signal('assignments', ['AssignmentGroup'])
        
        # Adding model 'Assignment'
        db.create_table('assignments_assignment', (
            ('id', orm['assignments.Assignment:id']),
            ('course', orm['assignments.Assignment:course']),
            ('group', orm['assignments.Assignment:group']),
            ('name', orm['assignments.Assignment:name']),
            ('due_date', orm['assignments.Assignment:due_date']),
            ('change_date', orm['assignments.Assignment:change_date']),
            ('possible_score', orm['assignments.Assignment:possible_score']),
            ('description', orm['assignments.Assignment:description']),
            ('submission_required', orm['assignments.Assignment:submission_required']),
        ))
        db.send_create_signal('assignments', ['Assignment'])
        
        # Adding model 'AssignmentSubmission'
        db.create_table('assignments_assignmentsubmission', (
            ('id', orm['assignments.AssignmentSubmission:id']),
            ('user', orm['assignments.AssignmentSubmission:user']),
            ('assignment', orm['assignments.AssignmentSubmission:assignment']),
            ('date', orm['assignments.AssignmentSubmission:date']),
            ('status', orm['assignments.AssignmentSubmission:status']),
            ('text', orm['assignments.AssignmentSubmission:text']),
            ('score', orm['assignments.AssignmentSubmission:score']),
        ))
        db.send_create_signal('assignments', ['AssignmentSubmission'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'AssignmentFileSubmission'
        db.delete_table('assignments_assignmentfilesubmission')
        
        # Deleting model 'AssignmentGroup'
        db.delete_table('assignments_assignmentgroup')
        
        # Deleting model 'Assignment'
        db.delete_table('assignments_assignment')
        
        # Deleting model 'AssignmentSubmission'
        db.delete_table('assignments_assignmentsubmission')
        
    
    
    models = {
        'assignments.assignment': {
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['courses.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': "orm['assignments.AssignmentGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'possible_score': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'submission_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'assignments.assignmentfilesubmission': {
            'assignment_submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_submissions'", 'to': "orm['assignments.AssignmentSubmission']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'assignments.assignmentgroup': {
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'weight': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'})
        },
        'assignments.assignmentsubmission': {
            'assignment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignment_submissions'", 'to': "orm['assignments.Assignment']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignment_submissions'", 'to': "orm['auth.User']"})
        },
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
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'courses.course': {
            'bulletin_board_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['assignments']
