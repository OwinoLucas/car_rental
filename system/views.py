from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse , HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Car, Order, PrivateMsg
from .forms import *
from .mpesa import lipa_na_mpesa
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)


def home(request):
    context = {
        "title" : "Car Rental"
    }
    return render(request,'home.html', context)

def login_view(request):
    form1 = UserLoginForm(request.POST or None)
    if form1.is_valid():
        username = form1.cleaned_data.get("username")
        password = form1.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if not request.user.is_staff:
            login(request, user)
            return redirect("/newcar/")
    return render(request, "form.html", {"form": form1, "title": "Login"})

def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()

        return redirect("/profile/")
    context = {
        "title" : "Registration",
        "form": form,
    }
    return render(request, "form.html", context)

def logout_view(request):
    logout(request)
    return render(request, "home.html", {})

def profile(request):
   
    if request.method == 'POST':
        u_form = UserForm(request.POST,instance=request.user)
        p_form = DriverForm(request.POST,request.FILES,instance=request.user.driver)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save() 
            messages.success(request, f'Your account has been updated!')
            return redirect('/login/')
    else:
        u_form = UserForm(instance=request.user)
        p_form = DriverForm(instance=request.user.driver)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        
    }
    return render(request, 'profile.html', context)


def car_list(request):
    car = Car.objects.all()

    query = request.GET.get('q')
    if query:
        car = car.filter(
                     Q(car_name__icontains=query) |
                     Q(company_name__icontains = query) |
                     Q(num_of_seats__icontains=query) |
                     Q(cost_par_day__icontains=query)
                            )

    # pagination
    paginator = Paginator(car, 12)  # Show 15 contacts per page
    page = request.GET.get('page')
    try:
        car = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        car = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        car = paginator.page(paginator.num_pages)
    context = {
        'car': car,
    }
    return render(request, 'car_list.html', context)

def car_detail(request, id=None):
    detail = get_object_or_404(Car,id=id)
    context = {
        "detail": detail
    }
    return render(request, 'car_detail.html', context)

def car_created(request):
    form = CarForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return HttpResponseRedirect("/")
    context = {
        "form" : form,
        "title": "Create Car"
    }
    return render(request, 'car_create.html', context)

def car_update(request, id=None):
    detail = get_object_or_404(Car, id=id)
    form = CarForm(request.POST or None, instance=detail)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
        "title": "Update Car"
    }
    return render(request, 'car_create.html', context)

def car_delete(request,id=None):
    query = get_object_or_404(Car,id = id)
    query.delete()

    car = Car.objects.all()
    context = {
        'car': car,
    }
    return render(request, 'admin_index.html', context)

#order
@login_required
def order_list(request):
    order = Order.objects.all()

    query = request.GET.get('q')
    if query:
        order = order.filter(
            Q(movie_name__icontains=query)|
            Q(employee_name__icontains=query)
        )

    # pagination
    paginator = Paginator(order, 4)  # Show 15 contacts per page
    page = request.GET.get('page')
    try:
        order = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        order = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        order = paginator.page(paginator.num_pages)
    context = {
        'order': order,
    }
    return render(request, 'order_list.html', context)

@login_required
def order_detail(request, id=None):
    detail = get_object_or_404(Order,id=id)
    due_date = detail.to
    from_date = detail.date
    day = (due_date - from_date).days
    cost = int(detail.car_name.cost_par_day)
    amount = cost * day
    
    context = {
        "detail": detail,
        "amount": amount
    }
    return render(request, 'order_detail.html', context)

@login_required
def payment(request, id=None):
    current_user = request.user.driver
    detail = get_object_or_404(Order,id=id)
    # price logic
    due_date = detail.to
    from_date = detail.date
    day = (due_date - from_date).days
    cost = int(detail.car_name.cost_par_day)
    amount = cost * day
    phoneNumber = current_user.phone_number
    if current_user:
        payment = lipa_na_mpesa(amount, phoneNumber)
        messages.success(request, f'You have successfully paid for out service!')
        return redirect("/car_list/")
    context = {
        "detail": detail,
        "amount": amount,
        "payment": payment,
        "current_user": current_user
    }
    return render(request, 'order_detail.html', context)

@login_required
def order_created(request):
    form = OrderForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
        "title": "Create Order"
    }
    return render(request, 'order_create.html', context)

@login_required
def order_update(request, id=None):
    detail = get_object_or_404(Order, id=id)
    form = OrderForm(request.POST or None, instance=detail)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
        "title": "Update Order"
    }
    return render(request, 'order_create.html', context)

@login_required
def order_delete(request,id=None):
    query = get_object_or_404(Order,id = id)
    query.delete()
    return HttpResponseRedirect("/listOrder/")

def newcar(request):
    new = Car.objects.order_by('-id')
    #seach
    query = request.GET.get('q')
    if query:
        new = new.filter(
            Q(car_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(num_of_seats__icontains=query) |
            Q(cost_par_day__icontains=query)
        )

    # pagination
    paginator = Paginator(new, 12)  # Show 15 contacts per page
    page = request.GET.get('page')
    try:
        new = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        new = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        new = paginator.page(paginator.num_pages)
    context = {
        'car': new,
    }
    return render(request, 'new_car.html', context)

def like_update(request, id=None):
    new = Car.objects.order_by('-id')
    like_count = get_object_or_404(Car, id=id)
    like_count.like+=1
    like_count.save()
    context = {
        'car': new,
    }
    return render(request,'new_car.html',context)

def popular_car(request):
    new = Car.objects.order_by('-like')
    # seach
    query = request.GET.get('q')
    if query:
        new = new.filter(
            Q(car_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(num_of_seats__icontains=query) |
            Q(cost_par_day__icontains=query)
        )

    # pagination
    paginator = Paginator(new, 12)  # Show 15 contacts per page
    page = request.GET.get('page')
    try:
        new = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        new = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        new = paginator.page(paginator.num_pages)
    context = {
        'car': new,
    }
    return render(request, 'new_car.html', context)

def contact(request):
    form = MessageForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        return HttpResponseRedirect("/car/newcar/")
    context = {
        "form": form,
        "title": "Contact With Us",
    }
    return render(request,'contact.html', context)

#-----------------Admin Section-----------------

def admin_car_list(request):
    car = Car.objects.order_by('-id')

    query = request.GET.get('q')
    if query:
        car = car.filter(
            Q(car_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(num_of_seats__icontains=query) |
            Q(cost_par_day__icontains=query)
        )

    # pagination
    paginator = Paginator(car, 12)  # Show 15 contacts per page
    page = request.GET.get('page')
    try:
        car = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        car = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        car = paginator.page(paginator.num_pages)
    context = {
        'car': car,
    }
    return render(request, 'admin_index.html', context)

def admin_msg(request):
    msg = PrivateMsg.objects.order_by('-id')
    context={
        "car": msg,
    }
    return render(request, 'admin_msg.html', context)

def msg_delete(request,id=None):
    query = get_object_or_404(PrivateMsg, id=id)
    query.delete()
    return HttpResponseRedirect("/message/")


# def getAccessToken(request):
#     consumer_key = 'v0z30UH3yG7p15oGdGQiAADMZadNwBF9'
#     consumer_secret = 'q7dKYsWqFiH7JT5Y'
#     api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

#     r = requests.get(api_URL, auth=HTTPBasicAuth(
#         consumer_key, consumer_secret))
#     mpesa_access_token = json.loads(r.text)
#     validated_mpesa_access_token = mpesa_access_token['access_token']

#     return HttpResponse(validated_mpesa_access_token)

# def lipa_na_mpesa_online(request):
#     access_token = MpesaAccessToken.validated_mpesa_access_token
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {
#     'Content-Type': 'application/json',
#     'Authorization': 'Bearer %s' % access_token
#     }
#     request = {
#         "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
#         "Password": LipanaMpesaPassword.decode_password,
#         "Timestamp": LipanaMpesaPassword.lipa_time,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": 1,
#         "PartyA": 254740237332,
#         "PartyB": LipanaMpesaPassword.Business_short_code,
#         "PhoneNumber": 254740237332,
#         "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
#         "AccountReference": "CAR RENTAL",
#         "TransactionDesc": "Testing stk push"
#     }

#     response = requests.post(api_url, json=request, headers=headers)
#     print(response.text)
#     return HttpResponse('success')
