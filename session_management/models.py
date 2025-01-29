from django.db import models



# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'event'


class Session(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING, related_name='sessions')
    track = models.ForeignKey('track.Track', on_delete=models.DO_NOTHING, related_name='track_sessions')
    date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    speaker = models.ManyToManyField('users.Speaker', related_name='speaker_session')

    class Meta:
        db_table = 'event_session'

    def __str__(self):
        return f'{self.name if self.name else self.event.name} - {self.track} - {self.date}'