from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Set roles for users'

    def handle(self, *args, **cmd_options):
      roles = {
         'admin': [
            'change_user',
            'view_user',
            'delete_user',
            'add_project',
            'change_project',
            'delete_project',
            'view_project',
            'view_comment',
            'add_comment',
            ],
         'editor': [
            'view_project',
            'add_project',
            'change_project',
            'delete_project',
            'view_comment',
            'add_comment',
          ],
         'user': [
            'view_project',
            'add_comment',
            'view_comment',
          ],
      }

      for role_name, permissions in roles.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        group.permissions.clear()
        for permission in permissions:
            try:
                permissionDb = Permission.objects.get(
                  codename=permission,
                )

                group.permissions.add(permissionDb)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Permission {permission} does not exist"))

        self.stdout.write(self.style.SUCCESS(f"Roles set for {role_name}"))