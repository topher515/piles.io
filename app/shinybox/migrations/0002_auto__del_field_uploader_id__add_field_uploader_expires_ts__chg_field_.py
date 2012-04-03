# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Uploader.id'
        db.delete_column('shinybox_uploader', 'id')

        # Adding field 'Uploader.expires_ts'
        db.add_column('shinybox_uploader', 'expires_ts',
                      self.gf('shinybox.models.ExpiresDateTimeField')(default=datetime.datetime(2012, 3, 30, 0, 0), db_index=True, blank=True),
                      keep_default=False)


        # Changing field 'Uploader.uuid'
        db.alter_column('shinybox_uploader', 'uuid', self.gf('shinybox.models.UUIDField')(max_length=64, primary_key=True))
        # Adding unique constraint on 'Uploader', fields ['uuid']
        db.create_unique('shinybox_uploader', ['uuid'])

        # Deleting field 'File.id'
        db.delete_column('shinybox_file', 'id')


        # Changing field 'File.uploader'
        db.alter_column('shinybox_file', 'uploader_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['shinybox.Uploader']))

        # Changing field 'File.expires_ts'
        db.alter_column('shinybox_file', 'expires_ts', self.gf('shinybox.models.ExpiresDateTimeField')(null=True))

        # Changing field 'File.uuid'
        db.alter_column('shinybox_file', 'uuid', self.gf('shinybox.models.UUIDField')(max_length=64, primary_key=True))
        # Adding unique constraint on 'File', fields ['uuid']
        db.create_unique('shinybox_file', ['uuid'])

    def backwards(self, orm):
        # Removing unique constraint on 'File', fields ['uuid']
        db.delete_unique('shinybox_file', ['uuid'])

        # Removing unique constraint on 'Uploader', fields ['uuid']
        db.delete_unique('shinybox_uploader', ['uuid'])


        # User chose to not deal with backwards NULL issues for 'Uploader.id'
        raise RuntimeError("Cannot reverse this migration. 'Uploader.id' and its values cannot be restored.")
        # Deleting field 'Uploader.expires_ts'
        db.delete_column('shinybox_uploader', 'expires_ts')


        # Changing field 'Uploader.uuid'
        db.alter_column('shinybox_uploader', 'uuid', self.gf('django.db.models.fields.CharField')(max_length=64))

        # User chose to not deal with backwards NULL issues for 'File.id'
        raise RuntimeError("Cannot reverse this migration. 'File.id' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'File.uploader'
        raise RuntimeError("Cannot reverse this migration. 'File.uploader' and its values cannot be restored.")

        # Changing field 'File.expires_ts'
        db.alter_column('shinybox_file', 'expires_ts', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'File.uuid'
        db.alter_column('shinybox_file', 'uuid', self.gf('django.db.models.fields.CharField')(max_length=64))
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
            'expires_ts': ('shinybox.models.ExpiresDateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'shiny_box': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files'", 'to': "orm['shinybox.ShinyBox']"}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'started_ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'success_ts': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'to': "orm['shinybox.Uploader']"}),
            'uuid': ('shinybox.models.UUIDField', [], {'max_length': '64', 'primary_key': 'True'})
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
            'expires_ts': ('shinybox.models.ExpiresDateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'uuid': ('shinybox.models.UUIDField', [], {'max_length': '64', 'primary_key': 'True'})
        }
    }

    complete_apps = ['shinybox']