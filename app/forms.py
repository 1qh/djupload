from django import forms

from .models import FileUpload


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ('file',)


class MultipleChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(MultipleChoiceForm, self).__init__(*args, **kwargs)
        self.fields['choices_field'] = forms.MultipleChoiceField(
            choices=[(x, x[8:]) for x in choices],
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'checkbox'},
            ),
        )
