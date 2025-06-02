from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Lead
import pytz

class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))


	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	




# Create Add Record Form
class AddRecordForm(forms.ModelForm):
    full_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Full Name", "class": "form-control"}),
        label=""
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"}),
        label=""
    )
    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Phone", "class": "form-control"}),
        label=""
    )
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Country", "class": "form-control"}),
        label=""
    )
    timezone = forms.ChoiceField(
        required=False,
        choices=[('', 'Select Timezone')] + [(tz, tz) for tz in pytz.all_timezones],
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )
    income_range = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Income Range", "class": "form-control"}),
        label=""
    )
    agent = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label=""
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Comment", "class": "form-control", "rows": 3}),
        label=""
    )
    agent_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Agent Comment", "class": "form-control", "rows": 2}),
        label="Agent Comment"
    )
    manager_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Manager Comment", "class": "form-control", "rows": 2}),
        label="Manager Comment"
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        if phone and not re.match(r'^\+?[\d\s\-()]{7,20}$', phone):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        import re
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise forms.ValidationError("Enter a valid email address.")
        return email

    class Meta:
        model = Lead
        fields = [
            "full_name",
            "email",
            "phone",
            "country",
            "timezone",
            "income_range",
            "agent",
            "comment",
            "agent_comment",
            "manager_comment",
        ]


class LeadImportForm(forms.Form):
    file = forms.FileField(
        label="Select CSV or Excel file",
        help_text="Upload a CSV or Excel file containing leads.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
