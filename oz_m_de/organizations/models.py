import operator

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import ugettext as _

COUNTRIES = (("NL", _("Netherlands")),
             ("DE", _("Germany")),
             ("BE", _("Belgium")))


class Address(models.Model):
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Postal_code"))
    city = models.CharField(max_length=255, verbose_name=_("City"))
    country = models.CharField(max_length=100, verbose_name=_("Country"), choices=COUNTRIES)

    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="addresses")

    class Meta:
        verbose_name = _("Address")


class OrganizationCategoryQuerySet(models.QuerySet):
    def has_active_organizations(self) -> QuerySet:
        """Organization categories that have at least one organization that is active, approved and not blocked.
        The organizations are ordered by name

        :return: Queryset containing Categories
        """
        categories = self.filter(organizations__is_active=True,
                                 organizations__is_blocked=False,
                                 organizations__is_approved=True).distinct()
        categories = categories.order_by("name")
        return categories


class OrganizationCategoryManager(models.Manager):
    def has_active_organizations(self) -> QuerySet:
        return self.get_queryset().has_active_organizations()

    def get_queryset(self) -> OrganizationCategoryQuerySet:
        return OrganizationCategoryQuerySet(self.model)


class OrganizationCategory(models.Model):
    objects = OrganizationCategoryManager()

    class Meta:
        verbose_name = _("Organization Category")
        verbose_name_plural = _("Organization categories")

    name = models.CharField(max_length=30, verbose_name="Name")
    rooms_available_applies = models.BooleanField(default=False, verbose_name=_("Rooms available"),
                                                  help_text=_(
                                                      "Does rooms available apply to this organization category?"))

    def __str__(self):
        return self.name


class DayOpeningHours(models.Model):
    open_first = models.TimeField(blank=True, null=True)
    close_first = models.TimeField(blank=True, null=True)
    open_second = models.TimeField(blank=True, null=True)
    close_second = models.TimeField(blank=True, null=True)


class OrganizationQuerySet(models.QuerySet):
    def is_active(self) -> QuerySet:
        """Get all organizations that are active, not blacked and approved"""
        return self.filter(is_active=True) \
            .filter(is_blocked=False) \
            .filter(is_approved=True)

    def is_active_and_category(self, category: OrganizationCategory) -> QuerySet:
        return self.is_active().filter(category=category).order_by("-is_member", "order", "name")

    def opened_today(self, category: OrganizationCategory = None) -> list:
        """Get a queryset containing all organizations of a certain category that are opened today

        :param category: category object
        :return: Queryset of organizations of the specified category that are opened today
        """
        if category:
            organizations = self.is_active_and_category(category)
        else:
            organizations = self.is_active()

        if organizations:
            return [o for o in organizations if o.open_today]
        return []

    def sorted_by_name(self) -> QuerySet:
        """
        :return: Queryset containing all organizations, sorted by name
        """
        return self.order_by("name")

    def sorted_by_order(self) -> QuerySet:
        """Sort all organizations by order, next by name

        :return: Queryset containing all organizations, sorted first by order, then by name
        """
        return self.order_by("order", "name")

    def sorted_by_name_for_owner(self, owner: User) -> QuerySet:
        """Get all the organizations for a certain owner and sort them by name

        :param owner: Owner of the organizations to return
        :return: Queryset containing organizations for the owner
        """
        return self.filter(owner=owner).order_by("name")


class OrganizationManager(models.Manager):
    def get_queryset(self):
        return OrganizationQuerySet(self.model)

    def is_active(self):
        return self.get_queryset().is_active()

    def is_active_and_category(self, category: OrganizationCategory) -> QuerySet:
        return self.get_queryset().is_active_and_category(category)

    def opened_today(self, branch=None):
        return self.get_queryset().opened_today(branch)

    def sorted_by_name(self):
        return self.get_queryset().sorted_by_name()

    def sorted_by_name_for_owner(self, owner: User):
        return self.get_queryset().sorted_by_name_for_owner(owner)

    def sorted_by_order(self) -> QuerySet:
        return self.get_queryset().sorted_by_order()


class Organization(models.Model):
    objects = OrganizationManager()

    class Meta:
        verbose_name = _("Organization")

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    category = models.ForeignKey(OrganizationCategory, on_delete=models.PROTECT, related_name="organizations",
                                 verbose_name=_("Category"))
    order = models.IntegerField(verbose_name=_("Order"), default=9999,
                                help_text=_("The order this organization will be displayed in the category. "
                                            "Organizations without this value will be ordered randomly."))
    phone_nr = models.CharField(max_length=30, verbose_name=_("Phone number"))

    website = models.URLField(blank=True, null=True, verbose_name=_("Website"),
                              help_text=_("Example: http://mywebsite.com or https://www.mywebsite.com"))

    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    owner = models.ForeignKey("users.User", related_name="organizations", verbose_name=_("Owner"))

    update_opening_hours_daily = models.BooleanField(default=False, verbose_name=_("Update opening hours daily"))
    today = models.OneToOneField(DayOpeningHours, blank=True, null=True, verbose_name=_("Today"))

    mon = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Monday"), related_name="organization_mon")
    tue = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Tuesday"), related_name="organization_tue")
    wed = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Wednesday"), related_name="organization_wed")
    thu = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Thursday"), related_name="organization_thu")
    fri = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Friday"), related_name="organization_fri")
    sat = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Saturday"), related_name="organization_sat")
    sun = models.OneToOneField(DayOpeningHours, blank=True, null=True,
                               verbose_name=_("Sunday"), related_name="organization_sun")

    is_active = models.BooleanField(default=True, verbose_name=_("Active"),
                                    help_text=_("Show the organization on the website"))
    is_approved = models.BooleanField(default=False, verbose_name=_("Approved"),
                                      help_text=_("The organization should be approved by the website administrator,"
                                                  "If approved, the organization will be shown on the website."))
    is_blocked = models.BooleanField(default=False, verbose_name=_("Blocked"),
                                     help_text=_("Organization is blocked and will not be shown on the website"))
    is_member = models.BooleanField(default=True, verbose_name=_("Member"), help_text=_("Is the organization a member"))

    rooms_available = models.BooleanField(default=False, verbose_name=_("Rooms available"),
                                          help_text=_("Are there currently rooms available?"))

    def __str__(self):
        return self.name

    @property
    def open_today(self) -> bool:
        """Check if the organization is open today, based on the value in open_first"""
        # Get the 3 letter day string in lowercase
        now = timezone.now().strftime("%a").lower()

        try:
            # If the organization has to enter the opening hours every day manually
            if self.update_opening_hours_daily:
                return True if self.today.open_first else False
            return True if getattr(self, now).open_first else False
        except AttributeError:
            return False

    @property
    def todays_opening_hours(self) -> DayOpeningHours:
        # Get the 3 letter day string in lowercase
        now = timezone.now().strftime("%a").lower()

        if self.update_opening_hours_daily:
            return self.today
        else:
            return getattr(self, now)
