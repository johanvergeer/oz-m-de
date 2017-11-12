# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, DeleteView

from .forms import (OrganizationForm, AddressForm, OpeningHoursForm, DAYS,
                    OrganizationAdminForm)
from .models import Organization, DayOpeningHours
from common.memberships import is_organizations_admin


class OrganizationCreateView(LoginRequiredMixin, TemplateView):
    template_name = "organizations/organization_form.html"

    def get_context_data(self, **kwargs):
        super(OrganizationCreateView, self).get_context_data(**kwargs)
        data = kwargs.get("data")
        context = {
            "organization_form": OrganizationForm(data=data),
            "address_form": AddressForm(data=data),
            "form_action": "create",
            "title": "Create organization"
        }

        return context

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        organization_form = OrganizationForm(data=request.POST)
        address_form = AddressForm(data=request.POST)

        if organization_form.is_valid() and address_form.is_valid():
            return self.forms_valid(organization_form, address_form)
        return self.forms_invalid(request.POST)

    def forms_valid(self, organization_form, address_form):
        organization = organization_form.save(commit=False)
        organization.owner = self.request.user

        organization.save()

        address = address_form.save(commit=False)
        address.country = "DE"
        address.organization = organization
        address.save()

        return redirect("organizations:list")

    def forms_invalid(self, data):
        ctx = self.get_context_data(data=data)
        return self.render_to_response(ctx)


class OrganizationUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "organizations/organization_form.html"

    def check_user(self, organization: Organization):
        user = self.request.user
        if is_organizations_admin(user):
            return
        if not organization.owner == user:
            raise PermissionDenied()

    def get_organization(self, pk):
        try:
            organization = Organization.objects.get(pk=pk)
            address = organization.addresses.first()
        except ObjectDoesNotExist:
            raise http.Http404()

        self.check_user(organization)

        return organization, address

    def get_organization_form(self, organization, data):
        user = self.request.user
        if is_organizations_admin(user):
            return OrganizationAdminForm(data=data, instance=organization)
        return OrganizationForm(data=data, instance=organization)

    def get_context_data(self, **kwargs):
        super(OrganizationUpdateView, self).get_context_data(**kwargs)

        pk = kwargs.get("pk")
        data = kwargs.get("data")

        organization, address = None, None

        if pk:
            organization, address = self.get_organization(pk)

        context = {
            "organization_form": self.get_organization_form(organization, data),
            "address_form": AddressForm(data=data, instance=address),
            "form_action": "update",
            "title": "Update organization",
            "pk": pk,
            "is_active": organization.is_active,
            "is_blocked": organization.is_blocked,
            "is_approved": organization.is_approved
        }

        if is_organizations_admin(self.request.user):
            context["owner_email"] = organization.owner.email

        return context

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        ctx = self.get_context_data(pk=pk)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        organization, address = self.get_organization(pk)
        organization_form = self.get_organization_form(organization, request.POST)
        address_form = AddressForm(data=request.POST, instance=address)

        if address_form.is_valid() and organization_form.is_valid():
            return self.is_valid(organization_form, address_form, pk)
        return self.is_invalid(request.POST)

    def is_valid(self, organization_form, address_form, pk):
        organization_form.save()
        address_form.save()

        ctx = self.get_context_data(pk=pk)
        return self.render_to_response(ctx)

    def is_invalid(self, data):
        ctx = self.get_context_data(data=data)
        return self.render_to_response(ctx)


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    # These next two lines tell the view to index lookups by username
    slug_field = 'pk'
    slug_url_kwarg = 'pk'


class OrganizationListView(LoginRequiredMixin, ListView):
    model = Organization

    def get_queryset(self):
        user = self.request.user

        if is_organizations_admin(user):
            return Organization.objects.sorted_by_order()
        return Organization.objects.sorted_by_name_for_owner(user)

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        context["is_organization_admin"] = is_organizations_admin(self.request.user)
        return context


class OrganizationDeleteView(LoginRequiredMixin, DeleteView):
    model = Organization
    success_url = reverse_lazy("organizations:list")

    template_name = "organizations/organization_delete.html"


class OrganizationOpeningHoursView(LoginRequiredMixin, TemplateView):
    template_name = "organizations/organization_opening_hours.html"

    def get(self, request, *args, **kwargs):
        organization_pk = kwargs.get("pk")
        organization = Organization.objects.get(pk=organization_pk)

        ctx = {"pk": organization_pk}

        if organization.update_opening_hours_daily:
            if organization.today:
                instance = organization.today
            else:
                instance = DayOpeningHours()
                instance.save()
                organization.today = instance
                organization.save()
            ctx["today_form"] = OpeningHoursForm(day="Today", instance=instance)

        else:
            for day, name in DAYS.items():
                if getattr(organization, day):
                    instance = getattr(organization, day)
                else:
                    instance = DayOpeningHours()
                    instance.save()
                    setattr(organization, day, instance)
                    organization.save()
                ctx["{}_form".format(day)] = OpeningHoursForm(prefix=day, instance=instance, day=name)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        organization_pk = kwargs.get("pk")
        organization = Organization.objects.get(pk=organization_pk)

        forms = {}

        if organization.update_opening_hours_daily:
            instance = organization.today
            forms["today_form"] = OpeningHoursForm(day="Today", data=request.POST, instance=instance)
        else:
            for day, name in DAYS.items():
                instance = getattr(organization, day)
                forms["{}_form".format(day)] = OpeningHoursForm(day=name, data=request.POST,
                                                                instance=instance, prefix=day)

        for form in forms.values():
            if not form.is_valid():
                return self.is_invalid(forms, organization_pk)
        return self.is_valid(forms, organization_pk, organization)

    def is_valid(self, forms, organization_pk, organization):
        for form in forms.values():
            form.save()
        forms["pk"] = organization_pk
        return self.render_to_response(forms)

    def is_invalid(self, forms, organization_pk):
        forms["pk"] = organization_pk
        return self.render_to_response(forms)


def rooms_available(request, *args, **kwargs):
    pk = kwargs.get("pk")

    organization = Organization.objects.get(pk=pk)
    organization.rooms_available = not organization.rooms_available
    organization.save()

    return redirect(reverse_lazy("organizations:list"))
