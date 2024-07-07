from django.db import models
from fcm_django.models import FCMDevice

# Create your models here.

class Subscription(models.Model):
    device = models.OneToOneField(FCMDevice, blank=False, primary_key=True, on_delete=models.CASCADE)
    threads = models.ManyToManyField('Thread', blank=True)
    GAKUGUNS = (
        (0,  '未設定'),
        (1, '人文・文化学群'),
        (2, '社会．国際学群'),
        (3, '人間学群'),
        (4, '生命環境学群'),
        (5, '理工学群'),
        (6, '情報学群'),
        (7, '医学群'),
        (8, '体育専門学群'),
        (9, '芸術専門学群'),
    )
    affiliation = models.IntegerField(choices=GAKUGUNS, verbose_name='所属学群', default=0)

    def __str__(self):
        return self.device.registration_id

class Thread(models.Model):
    thread_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.thread_id)