# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-26 14:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seqr', '0017_auto_20170623_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(db_index=True, max_length=30, unique=True)),
                ('created_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('last_modified_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('analysis_type', models.CharField(choices=[(b'ALIGN', b'Alignment'), (b'VARIANTS', b'Variant Calls'), (b'CNV', b'CNV Calls'), (b'BREAK', b'Breakpoints'), (b'SPLICE', b'Splice Junction Calls'), (b'ASE', b'Allele Specific Expression')], max_length=10)),
                ('is_loaded', models.BooleanField(default=False)),
                ('loaded_date', models.DateTimeField(blank=True, null=True)),
                ('source_file_path', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='samplebatch',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='samples',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='individual_id',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='is_loaded',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='loaded_date',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='sample_batch',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='source_file_path',
        ),
        migrations.AddField(
            model_name='project',
            name='genome_build_id',
            field=models.CharField(choices=[(b'37', b'GRCh37'), (b'38', b'GRCh38')], default=b'37', max_length=5),
        ),
        migrations.AddField(
            model_name='sample',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='seqr.Individual'),
        ),
        migrations.AddField(
            model_name='sample',
            name='sample_type',
            field=models.CharField(choices=[(b'WES', b'Exome'), (b'WGS', b'Whole Genome'), (b'RNA', b'RNA')], default='WES', max_length=3),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='locuslistentry',
            name='genome_build_id',
            field=models.CharField(choices=[(b'37', b'GRCh37'), (b'38', b'GRCh38')], default=b'37', max_length=5),
        ),
        migrations.AlterField(
            model_name='variantnote',
            name='genome_build_id',
            field=models.CharField(choices=[(b'37', b'GRCh37'), (b'38', b'GRCh38')], default=b'37', max_length=5),
        ),
        migrations.AlterField(
            model_name='varianttag',
            name='genome_build_id',
            field=models.CharField(choices=[(b'37', b'GRCh37'), (b'38', b'GRCh38')], default=b'37', max_length=5),
        ),
        migrations.DeleteModel(
            name='SampleBatch',
        ),
        migrations.AddField(
            model_name='dataset',
            name='samples',
            field=models.ManyToManyField(to='seqr.Sample'),
        ),
    ]
