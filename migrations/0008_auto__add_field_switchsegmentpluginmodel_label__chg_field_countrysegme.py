# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SwitchSegmentPluginModel.label'
        db.add_column(u'aldryn_segmentation_switchsegmentpluginmodel', 'label',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)


        # Changing field 'CountrySegmentPluginModel.label'
        db.alter_column(u'aldryn_segmentation_countrysegmentpluginmodel', 'label', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'CookieSegmentPluginModel.label'
        db.alter_column(u'aldryn_segmentation_cookiesegmentpluginmodel', 'label', self.gf('django.db.models.fields.CharField')(max_length=128))

    def backwards(self, orm):
        # Deleting field 'SwitchSegmentPluginModel.label'
        db.delete_column(u'aldryn_segmentation_switchsegmentpluginmodel', 'label')


        # Changing field 'CountrySegmentPluginModel.label'
        db.alter_column(u'aldryn_segmentation_countrysegmentpluginmodel', 'label', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'CookieSegmentPluginModel.label'
        db.alter_column(u'aldryn_segmentation_cookiesegmentpluginmodel', 'label', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

    models = {
        u'aldryn_segmentation.cookiesegmentpluginmodel': {
            'Meta': {'object_name': 'CookieSegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'cookie_key': ('django.db.models.fields.CharField', [], {'default': "'*'", 'max_length': '4096'}),
            'cookie_value': ('django.db.models.fields.CharField', [], {'default': "'*'", 'max_length': '4096'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        u'aldryn_segmentation.countrysegmentpluginmodel': {
            'Meta': {'object_name': 'CountrySegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'default': "'O1'", 'max_length': '2'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        u'aldryn_segmentation.segmentlimitpluginmodel': {
            'Meta': {'object_name': 'SegmentLimitPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'max_children': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'aldryn_segmentation.switchsegmentpluginmodel': {
            'Meta': {'object_name': 'SwitchSegmentPluginModel'},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'on_off': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
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
        }
    }

    complete_apps = ['aldryn_segmentation']