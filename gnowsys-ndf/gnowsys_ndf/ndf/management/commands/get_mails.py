from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = 'This fetches mails from a mailing list and if subscribed then also updates the same on the server'

	def handle(self, *args, **kwargs):
		print 'It does work'