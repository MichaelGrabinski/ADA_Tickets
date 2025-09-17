from django import forms
from .models import AdaRiderQ
class RiderSearchForm(forms.Form):
    by = forms.ChoiceField(choices=[('name','ADA Rider Name'), ('id','ADA Rider ID')], required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    ada_id = forms.CharField(required=False)
class RiderForm(forms.ModelForm):
    """
    Form bound to the AdaRiderQ model.  Since the database schema uses
    column names like fname/lname and aptstnum/aptstname, we map those
    directly.  A model form can still be used to update rows if your
    database user has write permissions, but the NEW_ID primary key must
    already exist.
    """
    class Meta:
        model = AdaRiderQ
        fields = [
            'fname',        # First Name
            'lname',        # Last Name
            'adaid',        # ADA ID
            'aptstnum',     # Street Number
            'aptstname',    # Street Name
            'aptunit',      # Apartment/Unit
            'zip',          # Zip code
            'Inactive',     # Inactive flag
            'Notes',        # Notes
        ]
        labels = {
            'fname': 'First Name',
            'lname': 'Last Name',
            'adaid': 'ADA ID',
            'aptstnum': 'Street Number',
            'aptstname': 'Street Name',
            'aptunit': 'Apt',
            'zip': 'Zip',
            'Inactive': 'Inactive',
            'Notes': 'Notes',
        }

from django import forms
from .models import AdaTicketPurchasesT

class TicketForm(forms.ModelForm):
    PAY_TYPE_CHOICES = [
        ("Cash", "Cash"),
        ("Check", "Check"),
    ]
    DEPT_ENTERED_BY_CHOICES = [
        ("YSS", "YSS"),
        ("SENIOR SERVICES", "Senior Services"),
    ]

    paytype = forms.ChoiceField(choices=PAY_TYPE_CHOICES, required=True)
    deptenter = forms.ChoiceField(choices=DEPT_ENTERED_BY_CHOICES, required=True)
    Notes = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)

    class Meta:
        model = AdaTicketPurchasesT
        fields = [
            'purdate', 'bkqty', 'puramt', 'paytype', 'chknum',
            'deptenter', 'Notes',
        ]
        widgets = {
            'purdate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
