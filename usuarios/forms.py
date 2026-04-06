from django import forms
from .models import Profile, Outing

# Form for creating and editing a user's profile.
# Each widget is explicitly styled with Bootstrap classes so the fields
# inherit the app's dark theme without any extra CSS.
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'city', 'age', 'interests', 'availability']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'interests': forms.TextInput(attrs={'class': 'form-control'}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


# Form for posting a new outing.
# Date and time inputs use the HTML5 native pickers (type="date" and type="time")
# so users get a calendar and clock without any extra JavaScript.
class OutingForm(forms.ModelForm):
    class Meta:
        model = Outing
        fields = ['place', 'date', 'time', 'description', 'city']
        widgets = {
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }