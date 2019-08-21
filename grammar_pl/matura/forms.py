from django import forms
from .models import Matura_Anwser

class Matura_Task_Anwser_Form(forms.ModelForm):
    #anwser = forms.ModelMultipleChoiceField(queryset=Matura_Task.anwser.objects.all())
    class Meta:
        model = Matura_Anwser
        fields = '__all__'