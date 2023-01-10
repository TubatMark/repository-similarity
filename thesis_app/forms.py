from django import forms
from .models import RepositoryFiles
from .models import RepositoryFiles, User, StudentUsers, TitleDefense, ProposalDefense, FinalDefense, Student, PanelUsers, Panel, Admin, AdminUsers
from django.contrib.auth.models import AbstractUser


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = RepositoryFiles
        fields = ["title", "proponents", "pdf_file"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-group"}),
            "proponents": forms.TextInput(attrs={"class": "form-group"}),
            "pdf_file": forms.FileInput(attrs={"class": "form-group"}),
        }


class StudentForm(forms.Form):
    # upload excel file for all enrolled students
    file = forms.FileField()


class TitleDefForm(forms.ModelForm):
    class Meta:
        model = TitleDefense
        fields = ["student_title", "student_proponents", "student_pdf_file"]
        widgets = {
            "student_title": forms.TextInput(attrs={"class": "form-group"}),
            "student_proponents": forms.TextInput(attrs={"class": "form-group"}),
            "student_pdf_file": forms.FileInput(attrs={"class": "form-group"}),
        }
        
class ProposalDefForm(forms.ModelForm):
    class Meta:
        model = ProposalDefense
        fields = ["student_title_p", "student_proponents_p", "student_pdf_file_p"]
        widgets = {
            "student_title_p": forms.TextInput(attrs={"class": "form-group"}),
            "student_proponents_p": forms.TextInput(attrs={"class": "form-group"}),
            "student_pdf_file_p": forms.FileInput(attrs={"class": "form-group"}),
        }
        
class FinalDefForm(forms.ModelForm):
    class Meta:
        model = FinalDefense
        fields = ["student_title_f", "student_proponents_f", "student_pdf_file_f"]
        widgets = {
            "student_title_f": forms.TextInput(attrs={"class": "form-group"}),
            "student_proponents_f": forms.TextInput(attrs={"class": "form-group"}),
            "student_pdf_file_f": forms.FileInput(attrs={"class": "form-group"}),
        }


class EditStudentForm(forms.ModelForm):
    model = StudentUsers
    fields = "__all__"

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-group"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-group"}))

    class Meta:
        model = Student
        fields = ['password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class PanelUsersForm(forms.ModelForm):
 
    class Meta:
        model = PanelUsers
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
        }

class AdminUsersForm(forms.ModelForm):
 
    class Meta:
        model = AdminUsers
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
        }
