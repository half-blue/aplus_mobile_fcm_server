from django.urls import path

from . import views
from . import apis

urlpatterns = [
    path('api/thread/<int:thread_id>/subscribe', apis.Subscribe.as_view(), name='add_subscribe'),
    path('api/device', apis.GetDevice.as_view(), name='get_device'),
    path('api/device/activate', apis.ActivateDevice.as_view(), name='activate_device'),
    path('api/device/subscription', apis.GetSubscription.as_view(), name='get_subscription'),
    path('api/thread/<int:thread_id>/unsubscribe', apis.Unsubscribe.as_view(), name='unsubscribe'),
    path('manage/app_endpoint', views.notice_manege_endpoint, name='notice_manage_endpoint'),
    path('manage/error', views.NoticeManegeErrorView.as_view(), name='notice_manage_error'),
    path('manage/', views.NoticeManegeIndexView.as_view(), name='notice_manage_index'),
    path('manage/unsubscribe_all', views.UnsubscribeAllThreads.as_view(), name='unsubscribe_all'),
    path('manage/register_affiliation', views.RegisteraffiliationView.as_view(), name='register_affiliation'),
]