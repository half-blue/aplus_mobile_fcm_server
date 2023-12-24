from django.core.management.base import BaseCommand
from firebase_admin.messaging import Message, Notification
from ...models import *


class Command(BaseCommand):
    help = "指定されたスレッドを購読しているユーザに通知する"

    def add_arguments(self, parser):
        parser.add_argument('thread_id', type=int, help='スレッドID', default=-1)
    
    def handle(self, *args, **options):
        thread_id = options['thread_id']
        targets = Subscription.objects.filter(threads__in=[thread_id])
        if not targets:
            # 指定されたスレッドIDを購読しているユーザはいない
            return
        
        # 通知を送信
        for target in targets:
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
            
        return