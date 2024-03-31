from django.core.management.base import BaseCommand
from firebase_admin.messaging import Message, Notification
from ...models import *
from django.conf import settings

class Command(BaseCommand):
    help = "指定されたスレッドを購読しているユーザに通知する"

    # 本番環境のFirebaseで動かすため、ローカル実行時は以下のスレッドのみ通知するように保険をかける
    DEBUG_THEARD_IDS = [123456789,]

    def add_arguments(self, parser):
        parser.add_argument('thread_id', type=int, help='スレッドID', default=-1)
    
    def handle(self, *args, **options):
        thread_id = options['thread_id']

        # DEBUGモードの場合はDEBUG_THEARD_IDSに指定されたスレッドのみ通知する
        if settings.DEBUG:
            print("DEBUGモードで実行中")
            if thread_id not in self.DEBUG_THEARD_IDS:
                print("DEBUGモードではDEBUG_THEARD_IDSに指定されたスレッドのみ通知します")
                print(f"指定されたスレッドIDはDEBUG_THEARD_IDSに含まれていません: {thread_id}")
                return
        # 指定されたスレッドIDを購読しているユーザを取得
        targets = Subscription.objects.filter(threads__in=[thread_id])
        if not targets:
            # 指定されたスレッドIDを購読しているユーザはいない
            return
        # 通知を送信
        for target in targets:
            try:
                target.device.send_message(
                    Message(
                        notification=Notification(
                            title='A+つくばに新しい投稿があります', 
                            body='タップして新しい投稿を確認しましょう',
                        ),
                        data={
                            'thread_id': str(thread_id), # str()でキャストしないとエラーになる
                        }
                    )
                )
            except Exception as e:
                print(f'通知の送信に失敗しました: {e}')
                continue
        return