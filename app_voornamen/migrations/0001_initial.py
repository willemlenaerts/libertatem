# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='m_be_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_be_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_be_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_be_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_br_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_br_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_br_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_br_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_vl_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_vl_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_vl_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_vl_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_wal_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_wal_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_wal_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='m_wal_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_be_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_be_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_be_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_be_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_br_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_br_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_br_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_br_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_vl_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_vl_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_vl_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_vl_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_wal_18',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_wal_18_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_wal_65',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='v_wal_alles',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Rang', models.IntegerField(default=0)),
                ('Voornaam', models.CharField(max_length=255)),
                ('Aantal', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='voornamen_lijst',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('Voornaam', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
