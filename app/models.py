from django.db import models
from fcm_django.models import FCMDevice

# Create your models here.

class Subscription(models.Model):
    device = models.OneToOneField(FCMDevice, blank=False, primary_key=True, on_delete=models.CASCADE)
    threads = models.ManyToManyField('Thread', blank=True)

    def __str__(self):
        return self.device.registration_id

class Thread(models.Model):
    thread_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.thread_id)