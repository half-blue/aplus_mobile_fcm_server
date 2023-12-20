from django.urls import path

from . import views
from . import apis

urlpatterns = [
    path('api/<int:thread_id>/subscribe', apis.Subscribe, name='add_subscribe'),
    path('api/device', apis.GetDevice, name='get_device'),
    path('api/device/activate', apis.ActivateDevice, name='activate_device'),
    path('api/device/subscription', apis.GetSubscription, name='get_subscription'),
]