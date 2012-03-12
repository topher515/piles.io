# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Uploader'
        db.create_table('piles_uploader', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('piles', ['Uploader'])

        # Adding model 'Pile'
        db.create_table('piles_pile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
        ))
        db.send_create_signal('piles', ['Pile'])

        # Adding M2M table for field admins on 'Pile'
        db.create_table('piles_pile_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pile', models.ForeignKey(orm['piles.pile'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('piles_pile_admins', ['pile_id', 'user_id'])

        # Adding M2M table for field participants on 'Pile'
        db.create_table('piles_pile_participants', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pile', models.ForeignKey(orm['piles.pile'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('piles_pile_participants', ['pile_id', 'user_id'])

        # Adding model 'Password'
        db.create_table('piles_password', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['piles.Pile'])),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('piles', ['Password'])

        # Adding model 'File'
        db.create_table('piles_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('filetype', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('pile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['piles.Pile'])),
            ('uploader', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['piles.Uploader'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('success', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('piles', ['File'])


    def backwards(self, orm):
        
        # Deleting model 'Uploader'
        db.delete_table('piles_uploader')

        # Deleting model 'Pile'
        db.delete_table('piles_pile')

        # Removing M2M table for field admins on 'Pile'
        db.delete_table('piles_pile_admins')

        # Removing M2M table for field participants on 'Pile'
        db.delete_table('piles_pile_participants')

        # Deleting model 'Password'
        db.delete_table('piles_password')

        # Deleting model 'File'
        db.delete_table('piles_file')


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
        'piles.file': {
            'Meta': {'object_name': 'File'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filetype': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'pile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['piles.Pile']"}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'success': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'uploader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['piles.Uploader']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'piles.password': {
            'Meta': {'object_name': 'Password'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['piles.Pile']"}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'piles.pile': {
            'Meta': {'object_name': 'Pile'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admin_piles'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'participant_piles'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'piles.uploader': {
            'Meta': {'object_name': 'Uploader'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['piles']
