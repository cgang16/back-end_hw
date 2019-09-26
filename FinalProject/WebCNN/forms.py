from django import forms


class UserForm(forms.Form):
    username = forms.CharField(max_length=128, required=True,
                               help_text='用户名只能包括0~9a~zA~z_', label='用户名',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '[A-Za-z0-9_]*',
                                                             'placeholder': 'Username', 'title': '用户名只能包括0~9a~zA~z_'}))
    password = forms.CharField(max_length=16, min_length=6, required=True,
                               help_text='密码长度6~16且不能包括空白符', label="密码",
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'pattern': r'\S{6,}',
                                                                 'placeholder': 'Password',
                                                                 'title': '密码长度6~16且不能包括空白符'}))


class LogonForm(forms.Form):
    username = forms.CharField(max_length=128, required=True,
                               help_text='用户名只能包括0~9a~zA~z_', label='用户名',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '[A-Za-z0-9_]*',
                                                             'placeholder': 'Username', 'title': '用户名只能包括0~9a~zA~z_'}))
    password1 = forms.CharField(max_length=16, min_length=6, required=True,
                                help_text='密码长度6~16且不能包括空白符', label="密码",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'pattern': r'\S{6,}',
                                                                  'placeholder': 'Password',
                                                                  'title': '密码长度6~16且不能包括空白符'}))
    password2 = forms.CharField(max_length=16, min_length=6, required=True,
                                help_text='密码长度6~16且不能包括空白符', label="确认密码",
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'pattern': r'\S{6,}',
                                                                  'placeholder': 'Password',
                                                                  'title': '密码长度6~16且不能包括空白符'}))


class ImageForm(forms.Form):
    image = forms.ImageField(label="选取本地图片", help_text="请上传一张JPEG图片",
                             widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'image'}))


class UrlForm(forms.Form):
    url = forms.URLField(label="使用URL", help_text="请输入一张JPEG图片的URL",
                         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'url'}))


class TimeForm(forms.Form):
    start_time = forms.DateTimeField(label="起始时间", required=True, input_formats=['%Y-%m-%dT%H:%M'],
                                     widget=forms.DateTimeInput(
                                         attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(label="结束时间", required=True, input_formats=['%Y-%m-%dT%H:%M'],
                                   widget=forms.DateTimeInput(
                                       attrs={'type': 'datetime-local'}))
