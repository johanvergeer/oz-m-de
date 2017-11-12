# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.OrganizationListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^create/$',
        view=views.OrganizationCreateView.as_view(),
        name='create'
    ),
    url(
        regex=r'^(?P<pk>[1-9]+)/$',
        view=views.OrganizationDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^delete/(?P<pk>[1-9]+)',
        view=views.OrganizationDeleteView.as_view(),
        name='delete'
    ),
    url(
        regex=r'^update/(?P<pk>[1-9]+)/$',
        view=views.OrganizationUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^opening-hours/(?P<pk>[1-9]+)/$',
        view=views.OrganizationOpeningHoursView.as_view(),
        name='opening-hours'
    ),
    url(
        regex=r'^rooms-available/(?P<pk>[1-9]+)/$',
        view=views.rooms_available,
        name='rooms-available'
    )
]
