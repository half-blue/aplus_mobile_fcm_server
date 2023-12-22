from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .serializers import *
from  .models import *

class GetSubscription(ListAPIView):
    """
    購読情報を取得する．
    セキュリティのためFCMトークンはheaderのX-HALFBLUE-FCM-TOKENに含めること．

    HTTP headers:
        X-HALFBLUE-FCM-TOKEN (str): FCMトークン
    """
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        fcm_token = self.request.headers.get('X-HALFBLUE-FCM-TOKEN')
        queryset = Subscription.objects.filter(device__registration_id = fcm_token)
        if queryset:
            return queryset
        else:   
            raise NotFound()

class GetDevice(ListAPIView):
    """
    デバイス情報を取得する．
    セキュリティのためFCMトークンはheaderのX-HALFBLUE-FCM-TOKENに含めること．

    HTTP headers:
        X-HALFBLUE-FCM-TOKEN (str): FCMトークン
    """
    serializer_class = FCMDeviceSerializer
    
    def get_queryset(self):
        fcm_token = self.request.headers.get('X-HALFBLUE-FCM-TOKEN')
        queryset = FCMDevice.objects.filter(registration_id = fcm_token)
        if queryset:
            return queryset
        else:
            raise NotFound()

class ActivateDevice(APIView):
    def patch(self, request):
        """
        デバイスを有効化・無効化する．

        セキュリティのためFCMトークンはheaderのX-HALFBLUE-FCM-TOKENに含めること．

        HTTP headers:
            X-HALFBLUE-FCM-TOKEN (str): FCMトークン

        JSON params:
            active (bool): 有効化・無効化
        """
        try:
            fcm_token = request.headers.get('X-HALFBLUE-FCM-TOKEN')
            device = FCMDevice.objects.get(registration_id = fcm_token)
        except FCMDevice.DoesNotExist:
            raise NotFound()
        
        device.active = request.data.get('active')
        try:
            device.save()
            return Response(status=200, data={"active": device.active})
        except:
            return Response(status=400, data={"error": "不正なリクエストです．"})

class Subscribe(APIView):

    def post(self, request, thread_id :int):
        """
        購読するスレッドを追加する．
        もし，サーバにトークンが登録されていなければエラーとなる．
        もし，サーバに購読情報が登録されていなければ新規登録する．
        もし，サーバにスレッドが登録されていなければ新規登録する．

        Args:
            thread_id (int): スレッドID

        HTTP headers:
            X-HALFBLUE-FCM-TOKEN (str): FCMトークン

        JSON params:
            device_type (str): デバイスの種類 'ios' or 'android' (新規登録時のみ参照されます)
    
        """
        # FCMトークンが存在するか確認(存在しなければ新規登録)
        try:
            fcm_token = request.headers.get('X-HALFBLUE-FCM-TOKEN')
            device = FCMDevice.objects.get(registration_id = fcm_token)
        except FCMDevice.DoesNotExist:
            device_type = request.data.get('device_type')
            if device_type not in ['ios', 'android']:
                return Response(status=400, data={"error": "device_typeは`ios`か`android`を指定してください．"})
            try:
                device = FCMDevice.objects.create(registration_id = fcm_token, type = device_type)
            except:
                return Response(status=400, data={"error": "不正なリクエストです．"})
        
        # スレッドが存在するか確認(存在しなければ新規登録)
        try:
            thread = Thread.objects.get(thread_id = thread_id)
        except Thread.DoesNotExist:
            thread = Thread.objects.create(thread_id = thread_id)
        
        # 購読を追加(購読テーブルが存在しなければ新規登録)
        # FYI: ManyToManyFieldのadd()は既に存在する場合は何もしない
        try:
            subscription = Subscription.objects.get(device = device)            
        except Subscription.DoesNotExist:
            subscription = Subscription.objects.create(device = device)
        subscription.threads.add(thread)

        return Response(status=201, data={"thread_id": thread_id})
