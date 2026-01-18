from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from api.models import Company, Employee, User


# This is so we can populate the DB with profiles for existing employees.
class Command(BaseCommand):
    help = "Automatically create employee profiles for existing Users"


    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        default_company = Company.objects.first()
        if default_company is None:
            raise CommandError("Company does not exist")

        users = User.objects.all()

        for user in users:
            #Skip users that already have an employee_profile
            if hasattr(user, 'employee_profile'):
                skipped_count += 1
                continue

            try:
                with transaction.atomic():
                    
                    Employee.objects.create(
                        user=user,
                        first_name=user.first_name or '',
                        last_name=user.last_name or '', 
                        email = user.email or '',
                        employee_code=100 + user.id,
                        salary=0,
                        company = default_company
                    )
                    created_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f'!!! Skipped user {user.username}: {e}'
                ))
        self.stdout.write(self.style.SUCCESS(
            f'Created {created_count} Employee profiles. Skipped {skipped_count} users.'
        ))