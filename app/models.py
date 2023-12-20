from django.db import models
from fcm_django.models import FCMDevice

# Create your models here.

class Subscription(models.Model):
    device = models.ForeignKey(FCMDevice, on_delete=models.CASCADE, primary_key=True)
    threads = models.ManyToManyField('Thread', blank=True)

    def __str__(self):
        return self.device.registration_id

class Thread(models.Model):
    thread_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.thread_id)