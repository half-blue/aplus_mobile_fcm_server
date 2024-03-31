from django.core.management.base import BaseCommand
from firebase_admin.messaging import Message, Notification
from ...models import *


class Command(BaseCommand):
    help = "指定されたスレッドを購読しているユーザに通知する"

    def add_arguments(self, parser):
        parser.add_argument('thread_id', type=int, help='スレッドID', default=-1)
        parser.add_argument('thread_title', type=str, help='スレッドタイトル', default='')
        parser.add_argument('body', type=str, help='投稿内容', default='')
        parser.add_argument('type', type=str, help='postかreplyか', default='post')
        parser.add_argument('post_id', type=str, help='post_id', default='')
        parser.add_argument('reply_id', type=str, help='reply_id', default='')
        
    
    def handle(self, *args, **options):
        thread_id = options['thread_id']
        targets = Subscription.objects.filter(threads__in=[thread_id])
        if not targets:
            # 指定されたスレッドIDを購読しているユーザはいない
            return
        
        title = options['thread_title']
        if options['type'] == 'post':
            title = f'{title}に新しい投稿があります'
        else:
            title = f'{title}に新しい返信があります'

        # 通知を送信
        for target in targets:
            try:
                target.device.send_message(
                    Message(
                        notification=Notification(
                            title=title, 
                            body=options['body'],
                        ),
                        data={
                            'thread_id': str(thread_id), # str()でキャストしないとエラーになる
                            'type': options['type'], # 'post' or 'reply'
                            'post_id': options['post_id'],
                            'reply_id': options['reply_id'],
                        }
                    )
                )
            except Exception as e:
                print(f'通知の送信に失敗しました: {e}')
                continue
        return