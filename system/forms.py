from django import forms
from .models import Car, Order, PrivateMsg, Driver
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,

)
User = get_user_model()
from .models import Driver

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This User doesnot Exist or Incorrect Password.")
            if not user.is_active:
                raise forms.ValidationError("This user is no longer active.")
        return super(UserLoginForm,self).clean(*args, **kwargs)

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]

class UserForm(forms.ModelForm):
    email = forms.EmailField()
   
    class Meta:
        model = User
        fields = [
            "username",
            "email"
        ]

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name','phone_number', 'id_number']

        def __init__(self, *args, **kwargs):
            super(DriverForm, self).__init__(*args, **kwargs)
            self.fields['phone_number'].widget.attrs['placeholder'] = self.fields['phone_number'].label or '2547XXXXXX'



class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "image",
            "car_name",
            "company_name",
            "num_of_seats",
            "cost_par_day",
            "content",
        ]

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "car_name",
            "driver",
            "cell_no",
            "address",
            "date",
            "to",
        ]

class MessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMsg
        fields = [
            "name",
            "email",
            "message",
        ]

