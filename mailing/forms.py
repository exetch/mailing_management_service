from django import forms
from django.forms import SelectDateWidget
from .models import Mailing, Message


class MailingForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=SelectDateWidget(attrs={'class': 'date-input'}),
    )
    end_date = forms.DateTimeField(
        widget=SelectDateWidget(attrs={'class': 'date-input'}),
    )

    class Meta:
        model = Mailing
        exclude = ['clients']

    def __init__(self, *args, **kwargs):
        super(MailingForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message

        fields = ['subject', 'body']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
