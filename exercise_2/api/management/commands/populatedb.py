import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Clean the database, create a superuser and populate the database with initial data for development"

    def handle(self, *args, **options):
        self.flush()
        self.create_superuser()
        self.load_fixtures()
        self.stdout.write(self.style.SUCCESS("Successfully populated the database!"))

    def flush(self):
        call_command("flush", "--no-input")
        self.stdout.write("Database flushed")

    def create_superuser(self):
        user = User.objects.create_superuser(
            username=os.environ.get("SUPER_USERNAME"),
            email=os.environ.get("SUPER_EMAIL"),
            password=os.environ.get("SUPER_PASSWORD"),
        )
        self.stdout.write(f"Created superuser: {user.username}")

    def load_fixtures(self):
        call_command("loaddata", os.environ.get("FIXTURE_NAME", "initial_data"))
        self.stdout.write("Database fixtures loaded")
