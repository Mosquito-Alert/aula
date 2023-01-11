from django import forms
from main.models import *
from django.forms import ModelForm
import unicodedata
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _
from main.models import QUIZ_TYPES
from tinymce.widgets import TinyMCE


class QuizForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    seq = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    html_header = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}))
    published = forms.BooleanField(label=_("Prova publicada?"),widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    requisite = forms.ModelChoiceField(label=_("Cal completar la prova del desplegable per poder fer aquesta prova"), queryset=Quiz.objects.all().order_by('name'), widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        userid = kwargs.pop('userid', None)
        inst = kwargs.pop('instance', None)
        qs = Quiz.objects.all()
        if userid:
            qs = qs.filter(author=userid)
        if inst:
            qs = qs.exclude(id=inst.id)
        self.fields['requisite'].queryset = qs.order_by('name')

    class Meta:
        model = Quiz
        fields = ['name', 'seq', 'html_header', 'published', 'requisite']



class QuizNewForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    seq = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    html_header = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}))
    published = forms.BooleanField(label=_("Prova publicada?"),widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    requisite = forms.ModelChoiceField(label=_("Cal completar la prova del desplegable per poder fer aquesta prova"),queryset=Quiz.objects.filter(campaign__active=True).order_by('name'),widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    type = forms.ChoiceField(choices=QUIZ_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        userid = kwargs.pop('userid', None)
        inst = kwargs.pop('instance', None)
        super(QuizNewForm, self).__init__(*args, **kwargs)
        qs = Quiz.objects.all()
        if userid:
            qs = qs.filter(author=userid)
        if inst:
            qs = qs.exclude(id=inst.id)
        self.fields['requisite'].queryset = qs.order_by('name')

    class Meta:
        model = Quiz
        fields = ['name', 'seq', 'published', 'html_header', 'requisite', 'type']


class QuizAdminForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    seq = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    published = forms.BooleanField(label=_("Prova publicada?"),widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=False)
    html_header = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}), required=False)
    requisite = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    type = forms.ChoiceField(choices=QUIZ_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    author = forms.ModelChoiceField(label=_("Autor"), queryset=User.objects.filter(profile__is_teacher=True).filter(profile__campaign__active=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Quiz
        fields = ['name', 'seq', 'html_header', 'published', 'type', 'author']


class EducationCenterForm(ModelForm):
    name = forms.CharField(label=_("Nom"), widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    hashtag = forms.CharField(label=_("Hashtag"), widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    location = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = EducationCenter
        fields = ['name','hashtag']


class SimplifiedGroupForm(ModelForm):
    password1 = forms.CharField(label=_("Password (Es recomana un password curt, de 4 caràcters:)"), strip=False,widget=forms.TextInput(attrs={'autocomplete': 'new-password', 'class': 'form-control','maxlength': 4}),)
    username = forms.CharField(label=_("Nom d'accés del grup (És similar a un nom d'usuari, curt, en minúscules i sense caràcters especials)"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control','maxlength': 150 }), )
    group_public_name = forms.CharField(label=_("Nom públic del grup"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control' }), )
    photo_path = forms.CharField(widget=forms.HiddenInput(), required=False)
    n_students_in_group = forms.IntegerField(label=_("Nombre d'estudiants al grup"),initial=3, widget=forms.NumberInput(attrs={'class': 'form-control' }))

    class Meta:
        model = User
        fields = ['username']

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
    teacher = forms.ModelChoiceField(label=_("Professor"), queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))
    in_group = forms.ModelChoiceField(label=_("Grup"), queryset=User.objects.filter(profile__is_group=True).all().order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))

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

    class Meta:
        model = User
        fields = ['username']


class AlumUpdateFormAdmin(AlumUpdateForm):
    teacher = forms.ModelChoiceField(label=_("Professor responsable"),queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username']


class SimplifiedAlumForm(ModelForm):
    password1 = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    password2 = forms.CharField(label=_("Repetir password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    username = forms.CharField(label=_("Nom usuari"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control'}), )
    teacher = forms.ModelChoiceField(label=_("Professor responsable"),queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))

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


class SimplifiedAlumFormForTeacher(ModelForm):
    password1 = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    password2 = forms.CharField(label=_("Repetir password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    username = forms.CharField(label=_("Nom usuari"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control'}), )

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


class SimplifiedAlumFormForAdmin(SimplifiedAlumFormForTeacher):
    teacher = forms.ModelChoiceField(label=_("Professor responsable"),queryset=User.objects.filter(profile__is_teacher=True).order_by('username'),widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username']




class SimplifiedTeacherForm(ModelForm):
    password1 = forms.CharField(label=_("Password"), strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),)
    password2 = forms.CharField(label=_("Repetir password"), strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}), )
    username = forms.CharField(label=_("Username"), strip=False,widget=forms.TextInput(attrs={'class': 'form-control' }), )
    belongs_to = forms.ModelChoiceField(label=_("Centre al que pertany"), queryset=EducationCenter.objects.filter(campaign__active=True).order_by('name'),widget=forms.Select(attrs={'class': 'form-control'}))

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
    belongs_to = forms.ModelChoiceField(label=_("Centre al que pertany"),queryset=EducationCenter.objects.filter(campaign__active=True).order_by('name'),widget=forms.Select(attrs={'class': 'form-control'}))

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
            raise forms.ValidationError(_('Els passwords són diferents! Si us plau torna a escriure\'ls'))
        return password_2


class QuestionUploadForm(forms.ModelForm):
    text = forms.CharField(label=_("Text que es mostrarà per solicitar la pujada d'un fitxer"), widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True)

    class Meta:
        model = Question
        fields = ("text",)


class QuestionPollForm(forms.ModelForm):
    question_order = forms.IntegerField(label=_("Ordre de la pregunta dins la prova"), required=True)
    text = forms.CharField(label=_("Text de la pregunta"), widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True)

    class Meta:
        model = Question
        fields = ("question_order","text")

    def clean_question_order(self):
        cleaned_data = self.cleaned_data.get('question_order')
        quiz_id = self.data.get('quiz_id',-1)
        if quiz_id != -1:
            questions = Question.objects.filter(quiz__id=int(quiz_id))
            for q in questions:
                if q.question_order == cleaned_data:
                    raise forms.ValidationError(_('Ja hi ha una pregunta amb aquest número d\'ordre per aquesta prova. Tria un número diferent'))
        return cleaned_data


class QuestionLinkForm(forms.ModelForm):
    question_order = forms.IntegerField(label=_("Ordre de la pregunta dins la prova"), required=True)
    text = forms.CharField(label=_("Text de la pregunta"), widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), required=True)
    doc_link = forms.CharField(label=_("Enllaç a document extern"), widget=forms.URLInput(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = Question
        fields = ("question_order","text","doc_link")

    def clean_question_order(self):
        cleaned_data = self.cleaned_data.get('question_order')
        quiz_id = self.data.get('quiz_id',-1)
        if quiz_id != -1:
            questions = Question.objects.filter(quiz__id=int(quiz_id))
            for q in questions:
                if q.question_order == cleaned_data:
                    raise forms.ValidationError(_('Ja hi ha una pregunta amb aquest número d\'ordre per aquesta prova. Tria un número diferent'))
        return cleaned_data


class QuestionForm(forms.ModelForm):
    question_order = forms.IntegerField(label=_("Ordre de la pregunta dins la prova"), required=True)
    text = forms.CharField(label=_("Text de la pregunta"), widget=forms.Textarea(attrs={'class': 'form-control','rows':4}), required=True)
    question_picture = forms.CharField(widget=forms.HiddenInput(), required=False)
    answers_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Question
        fields = ("question_order","text","answers_json")

    def clean_question_order(self):
        cleaned_data = self.cleaned_data.get('question_order')
        quiz_id = self.data.get('quiz_id',-1)
        if quiz_id != -1:
            questions = Question.objects.filter(quiz__id=int(quiz_id))
            for q in questions:
                if q.question_order == cleaned_data:
                    raise forms.ValidationError(_('Ja hi ha una pregunta amb aquest número d\'ordre per aquesta prova. Tria un número diferent'))
        return cleaned_data


class CampaignForm(forms.ModelForm):
    name = forms.CharField(label=_("Nom de la campanya"), strip=False, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    html_header_groups = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}), required=False)
    html_header_teachers = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}), required=False)
    start_date = forms.DateTimeField(input_formats=['%d/%m/%Y'], required=False, localize=True)
    end_date = forms.DateTimeField(input_formats=['%d/%m/%Y'], required=False, localize=True)

    class Meta:
        model = Campaign
        fields = ['name','start_date','end_date','html_header_groups','html_header_teachers']

    def clean_end_date(self):
        cleaned_data_start = self.cleaned_data.get('start_date')
        cleaned_data_end = self.cleaned_data.get('end_date')
        if cleaned_data_end is not None and cleaned_data_start is not None:
            if cleaned_data_start >= cleaned_data_end:
                raise forms.ValidationError(_('La data d\'inici no pot ser posterior o igual a la data de fi'))
        return cleaned_data_end
