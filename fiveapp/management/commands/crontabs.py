from django.core.management.base import BaseCommand
import logging

from fiveapp.crons.gcm_notification_crons import send_notification_before_five_mins_of_scheduled_call

logger = logging.getLogger('cron')

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--cron', help='Name of the cronjob')
        parser.add_argument('--arg', help='Arguments for crons if any')


    def handle(self, *args, **options):
        cron = options['cron']
        arg = options['arg']
        logger.info('Cron={}, arg={}'.format(cron, arg))

        if cron == 'send_notification_before_five_mins_of_scheduled_call':
            send_notification_before_five_mins_of_scheduled_call(arg)

