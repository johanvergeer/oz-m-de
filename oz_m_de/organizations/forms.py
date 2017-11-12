from django import forms
from django.core.exceptions import ValidationError
from django.db.models import ObjectDoesNotExist
from django.forms import modelform_factory
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML

from .models import Organization, Address, DayOpeningHours


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["address", "postal_code", "city"]

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ["update_opening_hours_daily", "today", "owner",
                   "mon", "tue", "wed", "thu", "fri", "sat", "sun",
                   "is_active", "is_blocked", "is_approved", "order",
                   "is_member"]

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        try:
            if not self.instance.category.rooms_available_applies:
                self.fields["rooms_available"].widget = HiddenInput()
        except ObjectDoesNotExist:
            self.fields["rooms_available"].widget = HiddenInput()


OrganizationAdminForm = modelform_factory(Organization, form=OrganizationForm,
                                          exclude=["today", "mon", "tue", "wed",
                                                   "thu", "fri", "sat", "sun"])

DAYS = {
    "mon": _("Monday"),
    "tue": _("Tuesday"),
    "wed": _("wednesday"),
    "thu": _("Thursday"),
    "fri": _("Friday"),
    "sat": _("Saturday"),
    "sun": _("Sunday")
}


class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = DayOpeningHours
        fields = "__all__"

    def __init__(self, day, *args, **kwargs):
        super(OpeningHoursForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Div(Div(HTML(day), css_class="col-md-1"),
                Div(
                    Div(
                        Div(
                            Div("open_first", css_class="col-md-6"),
                            Div("close_first", css_class="col-md-6"),
                            css_class="col-md-6"
                        ),
                        Div(
                            Div("open_second", css_class="col-md-6"),
                            Div("close_second", css_class="col-md-6"),
                            css_class="col-md-6"
                        ),
                        css_class="col-md-6"
                    ),
                    css_class="col-md-11"
                )
                ),
        )

        self.helper.disable_csrf = True
        self.helper.form_show_labels = False
        self.helper.form_tag = False

    def clean(self):
        open_first_value = self.cleaned_data.get("open_first") is not None
        close_first_value = self.cleaned_data.get("close_first") is not None
        open_second_value = self.cleaned_data.get("open_second") is not None
        close_second_value = self.cleaned_data.get("close_second") is not None
        if open_first_value and not close_first_value:
            raise ValidationError(_("Opening time requires a closing time"))
        if not open_first_value and close_first_value:
            raise ValidationError(_("Closing time requires an opening time"))
        if open_second_value and not close_second_value:
            raise ValidationError(_("Opening time requires a closing time"))
        if not open_second_value and close_second_value:
            raise ValidationError(_("Closing time requires an opening time"))
