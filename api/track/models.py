from django.db import models


class Venue(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    description = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'venue'
        unique_together = ('name', 'location')

# Create your models here.
class Track(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.DO_NOTHING, related_name='tracks')
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'track'
        unique_together = ('venue', 'name')