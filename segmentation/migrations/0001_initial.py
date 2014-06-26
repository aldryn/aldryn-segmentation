# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SegmentLimitPluginModel'
        db.create_table(u'segmentation_segmentlimitpluginmodel', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
            ('max_children', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'segmentation', ['SegmentLimitPluginModel'])

        # Adding model 'FallbackSegmentPluginModel'
        db.create_table(u'segmentation_fallbacksegmentpluginmodel', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
        ))
        db.send_create_signal(u'segmentation', ['FallbackSegmentPluginModel'])

        # Adding model 'SwitchSegmentPluginModel'
        db.create_table(u'segmentation_switchsegmentpluginmodel', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
            ('on_off', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'segmentation', ['SwitchSegmentPluginModel'])

        # Adding model 'CookieSegmentPluginModel'
        db.create_table(u'segmentation_cookiesegmentpluginmodel', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
            ('cookie_key', self.gf('django.db.models.fields.CharField')(default=u'', max_length=4096)),
            ('cookie_value', self.gf('django.db.models.fields.CharField')(default=u'', max_length=4096)),
        ))
        db.send_create_signal(u'segmentation', ['CookieSegmentPluginModel'])

        # Adding model 'AuthenticatedSegmentPluginModel'
        db.create_table(u'segmentation_authenticatedsegmentpluginmodel', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default=u'', max_length=128, blank=True)),
        ))
        db.send_create_signal(u'segmentation', ['AuthenticatedSegmentPluginModel'])


    def backwards(self, orm):
        # Deleting model 'SegmentLimitPluginModel'
        db.delete_table(u'segmentation_segmentlimitpluginmodel')

        # Deleting model 'FallbackSegmentPluginModel'
        db.delete_table(u'segmentation_fallbacksegmentpluginmodel')

        # Deleting model 'SwitchSegmentPluginModel'
        db.delete_table(u'segmentation_switchsegmentpluginmodel')

        # Deleting model 'CookieSegmentPluginModel'
        db.delete_table(u'segmentation_cookiesegmentpluginmodel')

        # Deleting model 'AuthenticatedSegmentPluginModel'
        db.delete_table(u'segmentation_authenticatedsegmentpluginmodel')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'segmentation.authenticatedsegmentpluginmodel': {
            'Meta': {'object_name': 'AuthenticatedSegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'})
        },
        u'segmentation.cookiesegmentpluginmodel': {
            'Meta': {'object_name': 'CookieSegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'cookie_key': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '4096'}),
            'cookie_value': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '4096'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'})
        },
        u'segmentation.fallbacksegmentpluginmodel': {
            'Meta': {'object_name': 'FallbackSegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'})
        },
        u'segmentation.segment': {
            'Meta': {'object_name': 'Segment', 'managed': 'False'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'segmentation.segmentlimitpluginmodel': {
            'Meta': {'object_name': 'SegmentLimitPluginModel', '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'max_children': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'segmentation.switchsegmentpluginmodel': {
            'Meta': {'object_name': 'SwitchSegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '128', 'blank': 'True'}),
            'on_off': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['segmentation']