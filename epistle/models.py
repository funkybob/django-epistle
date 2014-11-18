
from django.db import models
from django.db import transaction
from django.conf import settings
from django.utils.functional import cached_property
from django.utils import timezone


class ConversationQuerySet(models.QuerySet):
    def with_counts(self):
        return self.annotate(post_count=models.Count('messages'))

    def with_created(self):
        return self.annotate(created=models.Min('messages__created'))


class ConversationManager(models.Manager.from_queryset(ConversationQuerySet, 'ConversationManager')):

    def start_conversation(self, user, body):
        with transaction.atomic():
            conv = self.create(created_by=user)
            conv.participants.add(user)
            msg = Message.objects.craeat(conversation=conv, sender=user, body=body)
        return conv, msg


class Conversation(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')

    objects = ConversationManager()

    @cached_property
    def post_count(self):
        return self.messages.count()

    @cached_property
    def created(self):
        return self.messages.annotate(created=models.Min('created'))['created']

    def post(self, user, body):
        with transaction.atomic():
            msg = Message.objects.create(conversation=self, sender=user, body=body)
            self.participants.add(user)
        return msg


class Message(models.Model):
    conversation = models.ForeignKey('Conversation', related_mane='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages')
    created = models.DateTimeField(default=timezone.now)
    body = models.TextField(blank=True)

    def send_reply(self, user, body):
        self.conversation.post(user, body)
