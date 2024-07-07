from .models import Subscription
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView, View
from fcm_server.settings import DEBUG


# Create your views here.

def notice_manege_endpoint(request):
    """
    アプリからのリクエストを受け取り，FCMトークンをCookieに保存する．
    事前にSubscricriptionが存在している必要がある．
    現在はデフォルトでアプリが必ずSubscriptionを作成するようになっているが，仕様変更に注意．

    管理ページとトップにリダイレクトを行う．
    """
    fcm_token = request.GET.get('token')
    try:
        subscription = Subscription.objects.get(device__registration_id = fcm_token)
    except Subscription.DoesNotExist:
        redirect('notice_manage_error')
    response = redirect('notice_manage_index')
    is_tls_only = not DEBUG # 本番環境のみHTTPS時のみCookieを設定する
    response.set_cookie('fcm_token', fcm_token, max_age=60*60,
                         secure=is_tls_only, httponly=True, samesite='lax')
    return response
    
class NoticeManegeErrorView(TemplateView):
    template_name = 'app/auth_error.html'

class NoticeManegeIndexView(TemplateView):
    template_name = 'app/notice_manage_index.html'
    model = Subscription

    def get(self, request, *args, **kwargs):
        fcm_token = request.COOKIES.get('fcm_token')
        try:
            subscription = Subscription.objects.get(device__registration_id = fcm_token)
        except Subscription.DoesNotExist:
            return redirect('notice_manage_error')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        def get_gakugun_name(gakugun):
            return Subscription.GAKUGUNS[gakugun][1]

        context = super().get_context_data(**kwargs)
        fcm_token = self.request.COOKIES.get('fcm_token')
        subscription = Subscription.objects.get(device__registration_id = fcm_token) # 存在することが保証される
        context['gakugun'] = get_gakugun_name(subscription.affiliation)
        context["num_threads"] = subscription.threads.count()
        return context
    
@method_decorator(require_POST, name='dispatch')
class UnsubscribeAllThreads(View):
    def post(self, request, *args, **kwargs):
        fcm_token = request.COOKIES.get('fcm_token')
        try:
            subscription = Subscription.objects.get(device__registration_id = fcm_token)
        except Subscription.DoesNotExist:
            return redirect('notice_manage_error')
        subscription.threads.clear()
        return redirect('notice_manage_index')