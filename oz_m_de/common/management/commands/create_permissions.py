from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from oz_m_de.organizations.models import Organization


class Command(BaseCommand):
    help = "Create user permissions in the database"

    def handle(self, *args, **options):
        self.create_organization_admin_group()

    def create_organization_admin_group(self):
        organizations_admin_group, created = Group.objects.get_or_create(name="organizations_admin_group")
        organization_ct = ContentType.objects.get_for_model(Organization)

        update_organizations_permission = Permission.objects.create(codename="can_update_organizations",
                                                                    name="Can update organizations",
                                                                    content_type=organization_ct)

        organizations_admin_group.permissions.add(update_organizations_permission)

        self.stdout.write(self.style.SUCCESS("Successfully created organization admin group"))
