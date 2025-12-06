# users/management/commands/init_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

ROLE_DEFS = {
    "teacher": {
        "academics": ["view_subject", "view_homework", "add_homework", "change_homework"],
        "grades":    ["view_grade", "add_grade", "change_grade"],
        "attendance":["view_attendancerecord", "add_attendancerecord", "change_attendancerecord"],
        "events":    ["view_event", "add_event", "change_event"],
    },
    "student": {
        "academics": ["view_subject", "view_homework"],
        "grades":    ["view_grade"],
        "attendance":["view_attendancerecord"],
        "events":    ["view_event"],
    },
    "parent": {
        "academics": ["view_subject", "view_homework"],
        "grades":    ["view_grade"],
        "events":    ["view_event"],
    },
    # admin = superuser — групу не створюємо
}

class Command(BaseCommand):
    help = "Create/refresh role groups with baseline permissions."

    def handle(self, *args, **options):
        for role, app_perms in ROLE_DEFS.items():
            group, _ = Group.objects.get_or_create(name=role)
            perms_to_set = []
            for app_label, codenames in app_perms.items():
                for codename in codenames:
                    try:
                        perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                        perms_to_set.append(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Missing perm: {app_label}.{codename}"))
            group.permissions.set(perms_to_set)
            group.save()
            self.stdout.write(self.style.SUCCESS(f"Synced group: {role}"))
        self.stdout.write(self.style.SUCCESS("All role groups are in place."))
