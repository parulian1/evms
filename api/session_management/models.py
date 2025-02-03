from django.db import models

from api import track


# Create your models here.
class Event(models.Model):
    """
    based on techinasia concept, event should be allocated into a track so to prevents
    conflict was in event area
    """
    name = models.CharField(max_length=150)
    description = models.TextField()
    track = models.ForeignKey('track.Track', on_delete=models.DO_NOTHING, related_name='track_events')
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
    event = models.ManyToManyField(Event, related_name='sessions')
    speaker = models.ManyToManyField('users.Speaker', related_name='speaker_session')

    class Meta:
        db_table = 'event_session'

    def __str__(self):
        return f'{self.name}'


class Attendee(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, related_name='attendees')
    user = models.ForeignKey('users.User', on_delete=models.DO_NOTHING, related_name='user_attendee')
    purchaser_email = models.EmailField(blank=True, null=True)

    class Meta:
        db_table = 'attendee'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.session.name}'