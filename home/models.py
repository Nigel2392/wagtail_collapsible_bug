from django.db import models

from wagtail.models import Page


class HomePage(Page):
    pass

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property

from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    FieldRowPanel,
    MultiFieldPanel,
    TabbedInterface,
    ObjectList,
)

from modelcluster.models import ClusterableModel
from django.forms.formsets import BaseFormSet

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
)

from wagtail.models import Orderable
from modelcluster.fields import ParentalKey


class OfficeHours(Orderable):
    class WeekDays(models.TextChoices):
        MONDAY    = "1", _("Monday")
        TUESDAY   = "2", _("Tuesday")
        WEDNESDAY = "3", _("Wednesday")
        THURSDAY  = "4", _("Thursday")
        FRIDAY    = "5", _("Friday")
        SATURDAY  = "6", _("Saturday")
        SUNDAY    = "7", _("Sunday")

    office = ParentalKey(
        "Office",
        verbose_name=_("Office"),
        on_delete=models.CASCADE,
        related_name="hours",
    )

    day    = models.CharField(
        max_length=1,
        verbose_name=_("Day of Week"),
        help_text=_("Day of the week this time applies to."),
        choices=WeekDays.choices, 
        unique=True,
        blank=False,
        null=False,
    )
    open   = models.TimeField(
        verbose_name=_("Open Time"),
        help_text=_("Time the office opens."),
        blank=True, 
        null=True,
    )
    close  = models.TimeField(
        verbose_name=_("Close Time"),
        help_text=_("Time the office closes."),
        blank=True, 
        null=True,
    )
    closed = models.BooleanField(
        verbose_name=_("Closed"),
        help_text=_("Is the office closed on this day?"),
        default=False,
    )

    panels = [
        FieldRowPanel([
            FieldPanel("day"),
            FieldPanel("closed"),
        ]),
        FieldRowPanel([
            FieldPanel("open"),
            FieldPanel("close"),
        ]),
    ]

    class Meta:
        verbose_name = _("Office Hours")
        verbose_name_plural = _("Office Hours")
        ordering = ["day"]
        constraints = [
            # If closed is true, open and close should be null
            # If not closed and open is specified, close should also be specified and vice versa
            # Else they should both be null
            models.CheckConstraint(
                check=(
                    models.Q(closed=True) & models.Q(open__isnull=True) & models.Q(close__isnull=True)
                ) | (
                    models.Q(closed=False) & models.Q(open__isnull=False) & models.Q(close__isnull=False)
                ) | (
                    models.Q(closed=False) & models.Q(open__isnull=True) & models.Q(close__isnull=True)
                ),
                name="open_close",
            ),
        ]

    def save(self, *args, **kwargs):
        self.sort_order = int(self.day)
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        return super().clean()

    def __str__(self):
        day = self.get_day_display()
        if self.closed:
            return f"{day}: Closed"
        if self.open and self.close:
            return f"{day}: {self.open.strftime('%I:%M %p')} - {self.close.strftime('%I:%M %p')}"
        return f"{day}: Unknown"



class InlineOfficeHoursPanel(InlinePanel):
    def __init__(self, *args, **kwargs):
        kwargs["min_num"] = 7
        kwargs["max_num"] = 7
        super().__init__(*args, **kwargs)

    class BoundPanel(InlinePanel.BoundPanel):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for index, child in enumerate(self.children):
                child: MultiFieldPanel.BoundPanel
                if child.form.instance and not child.form.instance.day:
                    child.form.initial = {"day": index + 1}
                elif not child.form.instance:
                    child.form.initial = {"day": index + 1}
                child.form.fields["day"].widget.attrs["readonly"] = True # fix later

@register_setting
class Office(BaseSiteSetting, ClusterableModel):

    phone_number = models.CharField(
        verbose_name=_("Phone Number"),
        help_text=_("Phone number for the office."),
        max_length=20,
        blank=True,
        null=True,
    )

    fax_number = models.CharField(
        verbose_name=_("Fax Number"),
        help_text=_("Fax number for the office."),
        max_length=20,
        blank=True,
        null=True,
    )

    email_address = models.EmailField(
        verbose_name=_("Email Address"),
        help_text=_("Email address for the office."),
        max_length=255,
        blank=True,
        null=True,
    )

    panels = [
        FieldPanel("email_address"),
        FieldRowPanel([
            FieldPanel("phone_number"),
            FieldPanel("fax_number"),
        ]),
        InlineOfficeHoursPanel("hours", heading=_("Office Hours"), label=_("Day"), min_num=7, max_num=7),
    ]

    edit_handler = TabbedInterface([
        ObjectList(panels, heading=_("Office")),
    ])

    class Meta:
        verbose_name = _("Office")
        verbose_name_plural = _("Offices")

