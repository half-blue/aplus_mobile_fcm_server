from django.urls import path

from . import views
from . import apis

urlpatterns = [
    path('api/thread/<int:thread_id>/subscribe', apis.Subscribe.as_view(), name='add_subscribe'),
    path('api/device', apis.GetDevice.as_view(), name='get_device'),
    path('api/device/activate', apis.ActivateDevice.as_view(), name='activate_device'),
    path('api/device/subscription', apis.GetSubscription.as_view(), name='get_subscription'),
]