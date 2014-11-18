
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from django.utils import timezone


class ConversationQuerySet(models.QuerySet):
    def with_counts(self):
        return self.annotate(post_count=models.Count('messages'))
    def with_created(self):
        return self.annotate(created=models.Min('messages__created'))


class Conversation(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participating_in')

    objects = ConversationQuerySet.as_manager()

    @cached_property
    def post_count(self):
        return self.messages.count()
    @cached_property
    def created(self):
        return self.messages.annotate(created=models.Min('created'))['created']


class Message(models.Model):
    thread = models.ForeignKey('Conversation', related_mane='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages')
    created = models.DateTimeField(default=timezone.now)
    body = models.TextField(blank=True)

