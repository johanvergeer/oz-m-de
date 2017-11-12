from django.contrib.auth.models import User


def is_organizations_admin(user: User) -> bool:
    return user.groups.filter(name="organizations_admin_group").exists()
