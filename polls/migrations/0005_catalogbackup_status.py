# Generated by Django 3.2.13 on 2022-11-15 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_catalogbackup_metric_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogbackup',
            name='status',
            field=models.CharField(blank=True, choices=[('BACKING_UP', 'Backing Up'), ('RESTORING', 'Restoring')], max_length=10, null=True, verbose_name='Status'),
        ),
    ]
