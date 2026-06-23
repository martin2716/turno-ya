from django import forms
from app.models import Ausencia


class AusenciaForm(forms.ModelForm):
    class Meta:
        model = Ausencia
        fields = ["medico", "motivo", "fecha_inicio", "fecha_fin"]
        widgets = {
            "medico": forms.Select(attrs={"class": "form-select"}),
            "motivo": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def clean_motivo(self):
        motivo = self.cleaned_data.get("motivo")
        if not motivo or not motivo.strip():
            raise forms.ValidationError("El motivo es obligatorio.")
        return motivo.strip()

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise forms.ValidationError(
                "La fecha de fin no puede ser anterior a la de inicio."
            )
        return cleaned_data
