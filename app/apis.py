from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, MethodNotAllowed
from .serializers import *
from  .models import *

class GetSubscription(ListAPIView):
    """
    購読情報を取得する．
    """
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        fcm_token = self.kwargs['fcm_token']
        return Subscription.objects.filter(device__registration_id = fcm_token)

class GetDevice(ListAPIView):
    """
    デバイス情報を取得する．
    """
    serializer_class = FCMDeviceSerializer
    
    def get_queryset(self):
        fcm_token = self.request.query_params('fcm_token').get()
        return FCMDevice.objects.filter(registration_id = fcm_token)

class ActivateDevice(APIView):
    def patch(self, request, format=None):
        """
        デバイスを有効化する．

        HTTP params:
            fcm_token (str): FCMトークン
        """
        try:
            fcm_token = request.query_params('fcm_token').get()
            device = FCMDevice.objects.get(registration_id = fcm_token)
        except FCMDevice.DoesNotExist:
            raise NotFound()
        
        device.active = True
        device.save()
        return Response(status=200)

class Subscribe(APIView):

    def post(self, request, thread_id :int, format=None):
        """
        購読するスレッドを追加する．
        もし，サーバにトークンが登録されていなければエラーとなる．
        もし，サーバに購読情報が登録されていなければ新規登録する．
        もし，サーバにスレッドが登録されていなければ新規登録する．

        HTTP params:
            fcm_token (str): FCMトークン
            device_type (str): デバイスの種類 'ios' or 'android'
        
        Args:
            thread_id (int): スレッドID
        """
        # FCMトークンが存在するか確認(存在しなければ新規登録)
        try:
            fcm_token = request.query_params('fcm_token').get()
            device_type = request.query_params('device_type').get()
            device = FCMDevice.objects.get(registration_id = fcm_token)
        except FCMDevice.DoesNotExist:
            device = FCMDevice.objects.create(registration_id = fcm_token, type = device_type)
        
        # スレッドが存在するか確認(存在しなければ新規登録)
        try:
            thread = Thread.objects.get(thread_id = thread_id)
        except Thread.DoesNotExist:
            thread = Thread.objects.create(thread_id = thread_id)
        
        # 購読を追加(購読テーブルが存在しなければ新規登録)
        # FYI: ManyToManyFieldのadd()は既に存在する場合は何もしない
        try:
            subscription = Subscription.objects.get(device = device)
            subscription.threads.add(thread)
        except Subscription.DoesNotExist:
            subscription = Subscription.objects.create(device = device)
            subscription.threads.add(thread)
        
        return Response(status=201)
