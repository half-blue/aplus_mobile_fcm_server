from django.core.management.base import BaseCommand
from app.GAKUGUN_THREADS import GAKUGUN_THREADS
from ...models import Thread


class Command(BaseCommand):
    help = "GAKUGUN_THREADSに登録されているスレッドを登録する"

    def handle(self, *args, **options):
        for key, threads in GAKUGUN_THREADS.items():
            for t in threads:
                Thread.objects.get_or_create(thread_id=t)