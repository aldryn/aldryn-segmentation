# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_segmentation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authenticatedsegmentpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_segmentation_authenticatedsegmentpluginmodel', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='cookiesegmentpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_segmentation_cookiesegmentpluginmodel', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='fallbacksegmentpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_segmentation_fallbacksegmentpluginmodel', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='segmentlimitpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_segmentation_segmentlimitpluginmodel', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='switchsegmentpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_segmentation_switchsegmentpluginmodel', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
    ]
