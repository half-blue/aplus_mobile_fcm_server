# 学群登録がなされていないユーザに登録を催促する通知を送る
# 本番環境で実行しないこと

from django.core.management.base import BaseCommand
from firebase_admin.messaging import Message, Notification
from ...models import *

class Command(BaseCommand):
    help = "学群登録がなされていないユーザに登録を催促する通知を送る"
        
    def handle(self, *args, **options):
        targets = Subscription.objects.filter(affiliation=0)
        if not targets:
            # 学群登録がなされていないユーザはいない（多分あり得ない）
            return
        
        print(f"{len(targets)}人のユーザに通知を学群を尋ねる送信します。")

        # 通知を送信
        for target in targets:
            try:
                target.device.send_message(
                    Message(
                        notification=Notification(
                            title="あなたの学群を教えてください", 
                            body="A+つくばにあなたの学群を登録して、学生生活をより豊かにしましょう。",
                        ),
                        data={
                            'is_affiliation_redirect': 'true',
                        }
                    )
                )
            except Exception as e:
                print(f'通知の送信に失敗しました: {e}')
                continue
        return