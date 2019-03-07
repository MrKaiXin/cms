# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-03-05 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='头像url'),
        ),
        migrations.AddField(
            model_name='user',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='生日'),
        ),
        migrations.AddField(
            model_name='user',
            name='email_active',
            field=models.BooleanField(default=False, verbose_name='邮箱验证状态'),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.NullBooleanField(choices=[(True, '男'), (False, '女'), (None, '保密')], default=None, verbose_name='性别'),
        ),
        migrations.AddField(
            model_name='user',
            name='nick_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='昵称'),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='电话号码'),
        ),
    ]