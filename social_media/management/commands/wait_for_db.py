import time

from django.core.management.base import BaseCommand
from django.db import connections, OperationalError


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database connection ...")
        db_conn = None
        while db_conn is None:
            try:
                db_conn = connections["default"].cursor()
            except OperationalError:
                self.stdout.write("Database is unavailable, please wait ...")
                time.sleep(3)

        # Close the cursor to release the database connection
        db_conn.close()

        self.stdout.write(self.style.SUCCESS("Successfully connected"))
