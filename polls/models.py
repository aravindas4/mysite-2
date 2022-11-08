import datetime
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publilshed')


    def __str__(self) -> str:
        return self.question_text

    def save(self, *args, **kwargs):
        if self.pub_date is None:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.choice_text


from enum import Enum
import string

def humanize_str(string):
    return string.title().translate(str.maketrans({'_': ' ', '-': ' '}))

class CatalogBackup(models.Model):

    class CatalogStatus(str, Enum):
        BACKING_UP = "BACKING_UP"
        RESTORING = "RESTORING"

        @classmethod
        def choices(cls):
            return tuple((i.value, humanize_str(i.name)) for i in cls)
    
    biz = models.ForeignKey(
        Choice, related_name='catalog_backups', on_delete=models.CASCADE
    )
    updated_by = models.ForeignKey(
        Question, related_name="my_catalog_backups", blank=True, null=True,
        on_delete=models.SET_NULL
    )
    title = models.CharField("Title", max_length=255)
    description = models.TextField(
        "Description", blank=True, null=True, default=None
    )
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    backup_file = models.FileField(
        "Backup file", upload_to='catalog_backups/l/%Y/%m/%d',
        blank=True, null=True, default=None
    )

    metric_details = models.TextField(
        "Metric details", blank=True, null=True, default="{}"
    )

    status = models.CharField(
        "Status",  max_length=10, choices=CatalogStatus.choices(), 
        null=True, blank=True
    )

    class Meta:
        db_table = "atlas_catalogbackup"


@receiver(post_save, sender=Question)
def post_signal_for_question(sender, instance, **kwargs):
    pass 

@receiver(post_save, sender=Choice)
def post_signal_for_choice(sender, instance, **kwargs):
    pass
