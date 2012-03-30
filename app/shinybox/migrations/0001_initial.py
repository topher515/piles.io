# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Uploader'
        db.create_table('shinybox_uploader', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('shinybox', ['Uploader'])

        # Adding model 'ShinyBox'
        db.create_table('shinybox_shinybox', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal('shinybox', ['ShinyBox'])

        # Adding model 'Password'
        db.create_table('shinybox_password', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shinybox.ShinyBox'])),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('shinybox', ['Password'])

        # Adding model 'File'
        db.create_table('shinybox_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('filetype', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('shiny_box', self.gf('django.db.models.fields.related.ForeignKey')(related_name='files', to=orm['shinybox.ShinyBox'])),
            ('uploader', self.gf('django.db.models.fields.related.ForeignKey')(related_name='uploaders', to=orm['shinybox.Uploader'])),
            ('started_ts', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('success_ts', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expires_ts', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
        ))
        db.send_create_signal('shinybox', ['File'])

    def backwards(self, orm):
        # Deleting model 'Uploader'
        db.delete_table('shinybox_uploader')

        # Deleting model 'ShinyBox'
        db.delete_table('shinybox_shinybox')

        # Deleting model 'Password'
        db.delete_table('shinybox_password')

        # Deleting model 'File'
        db.delete_table('shinybox_file')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'shinybox.file': {
            'Meta': {'object_name': 'File'},
            'expires_ts': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'shiny_box': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['shinybox.ShinyBox']"}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'started_ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'success_ts': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploaders'", 'to': "orm['shinybox.Uploader']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'shinybox.password': {
            'Meta': {'object_name': 'Password'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shinybox.ShinyBox']"}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'shinybox.shinybox': {
            'Meta': {'object_name': 'ShinyBox'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'shinybox.uploader': {
            'Meta': {'object_name': 'Uploader'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['shinybox']