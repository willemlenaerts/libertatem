__author__ = 'Willem Lenaerts'

from django import forms

class NameForm(forms.Form):
    name = forms.CharField(label="Naam", max_length=100)

    birthyear = forms.ChoiceField(label="Geboortejaar",choices=[(x, x) for x in range(2015, 1920,-1)])

    GENDER_CHOICES = (
        ("man","Man"),("vrouw","Vrouw")
        )
    gender = forms.ChoiceField(label="Geslacht",choices=GENDER_CHOICES)
    LOCATION_CHOICES = (
    ("vlaanderen","Vlaanderen"),("wallonië","Wallonië")
    )
    location = forms.ChoiceField(label="Woonplaats",choices=LOCATION_CHOICES)
    