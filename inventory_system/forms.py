from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from inventory_system.models import Card, CardsList


class AddCardForm(ModelForm):
    class Meta:
        model = Card
        fields = ['num', 'name', 'price', 'note', 'photo']


class AddProductForm(ModelForm):
    model = forms.ModelChoiceField(queryset=Card.objects.all(), label='Модель', empty_label='Модель не выбрана')

    class Meta:
        model = CardsList
        fields = ['quantity', 'model']
        labels = {'quantity': 'Количество товара'}
