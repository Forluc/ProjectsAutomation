from django.core.management.base import BaseCommand
from teamapp.models import ProjectManager, FreeTimeTable


class Command(BaseCommand):
    help = 'Загрузка свободных слотов'

    def add_arguments(self, parser):
        parser.add_argument('week', help='Номер недели в месяце')

    def handle(self, *args, **options):
        for manager in ProjectManager.objects.all():
            start = manager.start_time
            end = manager.end_time
            time_to_add = start
            free_time, created = FreeTimeTable.objects.get_or_create(time=time_to_add, week=options['week'])
            free_time_count = free_time.count
            free_time.count = free_time_count + 3
            free_time.save(update_fields=['count'])
            while True:
                if end == time_to_add:
                    break
                else:
                    if time_to_add.minute == 30:
                        now_hour = time_to_add.hour
                        now_hour += 1
                        time_to_add = time_to_add.replace(hour=now_hour, minute=0)
                        free_time, created = FreeTimeTable.objects.get_or_create(time=time_to_add, week=options['week'])
                        free_time_count = free_time.count
                        free_time.count = free_time_count + 3
                        free_time.save(update_fields=['count'])
                    else:
                        time_to_add = time_to_add.replace(minute=30)
                        free_time, created = FreeTimeTable.objects.get_or_create(time=time_to_add, week=options['week'])
                        free_time_count = free_time.count
                        free_time.count = free_time_count + 3
                        free_time.save(update_fields=['count'])
        self.stdout.write('Свободные слоты были загружены в БД')
