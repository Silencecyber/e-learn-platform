from django import forms
from plattform import models
from plattform import xss_cleaner


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = ('name', 'description', 'image')
    def clean_name(self):
        user_content = self.cleaned_data['name']

        # Preventing cross site scripting attacks
        cleaned_data = xss_cleaner.clean_user_data(user_content)

        return cleaned_data

    def clean_description(self):
        user_content = self.cleaned_data['description']

        # Preventing cross site scripting attacks
        cleaned_data = xss_cleaner.clean_user_data(user_content)

        return cleaned_data


class ModuleForm(forms.ModelForm):
    class Meta:
        model = models.Module
        fields = '__all__'


class TopicForm(forms.ModelForm):
    class Meta:
        model = models.Topic
        fields = ('content',)

    def clean_content(self):
        user_content = self.cleaned_data['content']

        # Preventing cross site scripting attacks
        cleaned_data = xss_cleaner.clean_user_data(user_content)

        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ('image', 'about')


class QuizForm(forms.ModelForm):
    class Meta:
        model = models.Quiz
        fields = ('name',)
