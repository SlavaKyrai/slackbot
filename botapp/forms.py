from django.contrib.auth.models import User
from django import forms

from botapp.models import WorkSpace


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ChannelConfigForm(forms.ModelForm):

    def __init__(self, channels, *args, **kwargs):
        super(ChannelConfigForm, self).__init__(*args, **kwargs)
        self.fields['announcing_channel_name'].choices = channels  # get channels from view

    announcing_channel_name = forms.ChoiceField(choices=(), widget=forms.RadioSelect())

    class Meta:
        model = WorkSpace
        fields = ['announcing_channel_name']


class AddModeratorForm(forms.ModelForm):
    class Meta:
        model = WorkSpace
        fields = ['moderators']
