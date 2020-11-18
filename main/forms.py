from django import forms
from main.models import *
from django.forms import ModelForm
import unicodedata
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _


class QuizForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    class Meta:
        model = Quiz
        fields = ['name']


class EducationCenterForm(ModelForm):
    name = forms.CharField(label=_("Nom"), widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    location = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = EducationCenter
        fields = ['name']


class SimplifiedGroupForm(ModelForm):
    password1 = forms.CharField(label=_("Password (Es recomana un password curt, de 4 caràcters:)"), strip=False,widget=forms.TextInput(attrs={'autocomplete': 'new-password', 'class': 'form-control','maxlength': 4}),)
    username = forms.CharField(label=_("Nom d'accés del grup (És similar a un nom d'usuari, curt, en minúscules i sense caràcters especials)"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control','maxlength': 150 }), )
    group_public_name = forms.CharField(label=_("Nom públic del grup"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control' }), )
    photo_path = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['username']

    # def clean_password2(self):
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise ValidationError(
    #             self.error_messages['password_mismatch'],
    #             code='password_mismatch',
    #         )
    #     return password2
    #
    # def _post_clean(self):
    #     super()._post_clean()
    #     # Validate the password after self.instance is updated with form data
    #     # by super().
    #     password = self.cleaned_data.get('password2')
    #     if password:
    #         try:
    #             password_validation.validate_password(password, self.instance)
    #         except ValidationError as error:
    #             self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class SimplifiedAlumForm(ModelForm):
    password1 = forms.CharField(label=_("Password"), strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),)
    password2 = forms.CharField(label=_("Repetir password"), strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    username = forms.CharField(label=_("Nom usuari"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control' }), )
    teacher = forms.ModelChoiceField(label="Professor", queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))
    in_group = forms.ModelChoiceField(label="Grup", queryset=User.objects.filter(profile__is_group=True).all().order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AlumUpdateForm(ModelForm):
    username = forms.CharField(label=_("Nom usuari"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control'}), )
    teacher = forms.ModelChoiceField(label="Professor responsable",queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username']


class SimplifiedAlumForm(ModelForm):
    password1 = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    password2 = forms.CharField(label=_("Repetir password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    username = forms.CharField(label=_("Nom usuari"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control'}), )
    teacher = forms.ModelChoiceField(label="Professor responsable",queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class SimplifiedTeacherForm(ModelForm):
    password1 = forms.CharField(label=_("Password"), strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),)
    password2 = forms.CharField(label=_("Repetir password"), strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    username = forms.CharField(label=_("Username"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control' }), )
    belongs_to = forms.ModelChoiceField(label="Centre al que pertany", queryset=EducationCenter.objects.all().order_by('name'),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user




class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super().to_python(value))

    def widget_attrs(self, widget):
        return {
            **super().widget_attrs(widget),
            'autocapitalize': 'none',
            'autocomplete': 'username',
        }


class TeacherForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class TeacherUpdateForm(forms.ModelForm):
    username = forms.CharField(label=_("Username"), strip=False, widget=forms.TextInput(attrs={'class': 'form-control'}), )
    belongs_to = forms.ModelChoiceField(label="Centre al que pertany",queryset=EducationCenter.objects.all().order_by('name'),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}


class ChangePasswordForm(forms.Form):
    password_1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    def clean_password_2(self):
        cleaned_data = self.cleaned_data
        password_2 = cleaned_data.get('password_2')
        password_1 = cleaned_data.get('password_1')
        if password_1 != password_2:
            raise forms.ValidationError('Els passwords són diferents! Si us plau torna a escriure\'ls')
        return password_2