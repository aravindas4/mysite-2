import datetime
from django.db import models
from pytz import timezone

from django.db.models.signals import post_signal
from django.dispatch import receiver


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date publilshed')


    def __str__(self) -> str:
        return self.question_text

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


@receiver(post_signal, sender=Question)
def post_signal_for_question(sender, instance, **kwargs):
    pass 

@receiver(post_signal, sender=Choice)
def post_signal_for_choice(sender, instance, **kwargs):
    pass
