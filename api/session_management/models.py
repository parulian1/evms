from django.db import models

from api.utils.choices import Responsibility


# Create your models here.
class Speaker(models.Model):

    profile = models.ForeignKey('users.Profile', on_delete=models.DO_NOTHING, related_name='speaker_profile')
    role = models.CharField(
        choices=Responsibility.choices,
        max_length=50,
        blank=True,
        default=Responsibility.HOST
    )

    class Meta:
        db_table = 'speaker'

    def __str__(self):
        return f'{self.profile.get_full_name()} - {self.role}'


class Event(models.Model):
    """
    based on techinasia concept, event should be allocated into a track so to prevents
    conflict was in event area
    """
    name = models.CharField(max_length=150)
    description = models.TextField()
    track = models.ForeignKey('track.Track', on_delete=models.DO_NOTHING, related_name='track_events')
    speakers = models.ManyToManyField('Speaker', related_name='speaker_events')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.IntegerField() # should be less than track capacity

    def __str__(self):
        return f'{self.name} - {self.track.name} - {self.date.isoformat()}'

    class Meta:
        db_table = 'event'


class Session(models.Model):
    """
    session should manage which event that belong to its own and also speaker, etc.
    """
    name = models.CharField(max_length=150, blank=True, null=True)
    events = models.ManyToManyField(Event, related_name='sessions')

    class Meta:
        db_table = 'event_session'

    def __str__(self):
        return f'{self.name}'

    def get_capacity(self):
        return self.events.aggregate(models.Sum('capacity'))['capacity__sum']


class Attendee(models.Model):
    session = models.ForeignKey('session_management.Session', on_delete=models.DO_NOTHING, related_name='attendees')
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='user_attendee')
    purchaser_email = models.EmailField(blank=True, null=True)
    purchaser_first_name = models.CharField(max_length=100, blank=True, null=True)
    purchaser_last_name = models.CharField(max_length=100, blank=True, null=True)
    purchaser_phone_number = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        db_table = 'session_attendee'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.session.name}'