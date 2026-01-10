from django import forms
from .models import Film


class FilmSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Название фильма, режиссер...",
            }
        ),
    )
    genre = forms.ChoiceField(
        required=False,
        label="Жанр",
        choices=[("", "Все жанры")] + Film.GENRE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    year = forms.IntegerField(
        required=False,
        label="Год",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Год выпуска"}
        ),
    )
    emotions = forms.ModelMultipleChoiceField(
        required=False,
        queryset=None,
        label="Эмоции",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from emotions.models import Emotion

        self.fields["emotions"].queryset = Emotion.objects.filter(is_active=True)
