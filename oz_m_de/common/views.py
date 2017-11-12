from django.utils import timezone
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from oz_m_de.organizations.models import Organization, OrganizationCategory


def getkey(item: OrganizationCategory) -> str:
    return item.name


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get(self, request, *args, **kwargs):
        category_id = request.GET.get("category")
        category = None
        if category_id:
            category = get_object_or_404(OrganizationCategory, pk=category_id)
            organizations = Organization.objects.is_active_and_category(category)
            categories = None
        else:
            organizations = None
            categories = OrganizationCategory.objects.has_active_organizations()

        day = timezone.now().strftime("%a").lower

        ctx = {
            "category": category,
            "organizations": organizations,
            "day": day,
            "organization_types": categories
        }

        return self.render_to_response(ctx)
