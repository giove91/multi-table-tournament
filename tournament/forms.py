from django import forms
from django.core.exceptions import ValidationError


ERROR_MESSAGES = {
    'required': 'Completare questo campo.',
    'max_length': 'Questo nome è troppo lungo.',
    'invalid': 'Inserisci un valore valido.'
}

def validate_captcha(value):
    if value != 0:
        raise ValidationError(
            'Risposta errata.'
        )

class RegistrationForm(forms.Form):
    team_name = forms.CharField(max_length=25, label='Nome della squadra', error_messages=ERROR_MESSAGES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in range(6):
            self.fields['player_{}'.format(i)] = forms.CharField(
                max_length=64,
                required=(i == 0),  # only the first player is required
                label='Giocatore {}{}'.format(i+1, ' (capitano)' if i == 0 else ''),
                empty_value=None,
                error_messages=ERROR_MESSAGES,
            )

        self.fields['captcha'] = forms.IntegerField(
            label='Captcha: quanti sono i numeri primi pari maggiori di 42?',
            label_suffix='',
            error_messages=ERROR_MESSAGES,
            validators=[validate_captcha]
        )
