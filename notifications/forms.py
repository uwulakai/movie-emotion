from django import forms
from .models import Subscription
from emotions.models import Emotion


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["emotion", "min_intensity"]
        widgets = {
            "emotion": forms.Select(attrs={"class": "form-select"}),
            "min_intensity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 10,
                    "type": "range",
                    "step": 1,
                }
            ),
        }
        labels = {
            "emotion": "Эмоция",
            "min_intensity": "Минимальная интенсивность",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["emotion"].queryset = Emotion.objects.filter(is_active=True)
