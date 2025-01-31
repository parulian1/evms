from django.db import models

# Create your models here.
class Track(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    is_available = models.BooleanField()
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'track'