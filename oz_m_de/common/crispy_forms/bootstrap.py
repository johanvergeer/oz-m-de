from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import LayoutObject, Submit, HTML
from django.utils.translation import ugettext as _


class SubmitCancelFormActions(LayoutObject):
    """Custom bootstrap layout object. It wraps a Cancel anchor tag and a Submit
    input field in a <div class="form-actions">.

    Example::

        SubmitCancelFormActions(cancel_href="/some/url/")
    """
    def __init__(self, cancel_href, *fields, **kwargs):
        cancel_href = cancel_href
        self.cancel_href = "{{% url '{0}' %}}".format(cancel_href) if cancel_href != "#" else cancel_href

    def render(self, form, form_style, context, **kwargs):
        cancel = _("Cancel")
        layout_object = FormActions(
            HTML("""<a role="button" class="btn btn-default" href="{0}">{1}</a>""".format(self.cancel_href, cancel)),
            Submit('save', _('Save')),
        )
        return layout_object.render(form, form_style, context, **kwargs)
