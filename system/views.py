from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse , HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Car, Order, PrivateMsg
from .forms import *
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model,
)
from .mpesa import lipa_na_mpesa
from django.contrib.messages import constants as messages
from django.contrib import messages


def home(request):
    context = {
        "title" : "Car Rental"
    }
    return render(request,'home.html', context)

def register_view(request):
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()

        return redirect("login")
    context = {
        "title" : "Registration",
        "form": form,
    }
    return render(request, "form.html", context)

def login_view(request):
    form1 = UserLoginForm(request.POST or None)
    if form1.is_valid():
        username = form1.cleaned_data.get("username")
        password = form1.cleaned_data.get("password")
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Your logged in!')
            return redirect("profile")
    return render(request, "form.html", {"form": form1, "title": "Login"})


def logout_view(request):
    logout(request)
    return render(request, "home.html", {})

def profile(request):
    current_user = request.user
    if current_user:
        if request.method == 'POST':
            u_form = UserForm(request.POST,instance=request.user)
            p_form = DriverForm(request.POST,request.FILES,instance=request.user.driver)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save() 
                messages.success(request, f'Your account has been updated!')
                return redirect('newcar')
        else:
            u_form = UserForm(instance=request.user)
            p_form = DriverForm(instance=request.user.driver)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'current_user': current_user,
        
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

@login_required
def user_list(request):
    drivers = Driver.objects.all()

    query = request.GET.get('q')
    if query:
        drivers = drivers.filter(
            Q(username__icontains=query)|
            Q(first_name__icontains=query)|
            Q(last_name__icontains=query)
        )

    # pagination
    paginator = Paginator(drivers, 4)  # Show 15 contacts per page
    page = request.GET.get('page')
    try:
        drivers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        drivers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        drivers = paginator.page(paginator.num_pages)
    context = {
        'drivers': drivers,
    }
    return render(request, 'driver_list.html', context)

#order
@login_required
def order_list(request):
    order = Order.objects.all()

    query = request.GET.get('q')
    if query:
        order = order.filter(
            Q(car_name__icontains=query)|
            Q(driver__icontains=query)
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
def your_order_list(request):
    current_user = request.user.driver
    if current_user:
        order = Order.objects.filter(driver=current_user)


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
        'current_user': current_user,
        'order': order,
    }
    return render(request, 'your_orders.html', context)

@login_required
def order_detail(request, id=None):
    current_user = request.user.driver
    if current_user:
        detail = get_object_or_404(Order,id=id)
        driver = current_user
        dials = current_user.phone_number
        due_date = detail.to
        from_date = detail.date
        day = (due_date - from_date).days
        cost = int(detail.car_name.cost_par_day)
        amount = cost * day
    
    context = {
        "detail": detail,
        "amount": amount,
        "driver": driver,
        "dials": dials
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
def payment(request, id=None):
    current_user = request.user.driver
    if current_user:
        detail = get_object_or_404(Order,id=id)
        # price logic
        due_date = detail.to
        from_date = detail.date
        day = (due_date - from_date).days
        cost = int(detail.car_name.cost_par_day)
        amount = cost * day
        phoneNumber = current_user.phone_number
    
        payment = lipa_na_mpesa(amount, phoneNumber)
        messages.success(request, f'You have successfully paid for our service!')
        return redirect("your_order_list")
    context = {
        "detail": detail,
        "amount": amount,
        "payment": payment,
        "current_user": current_user
    }
    return render(request, 'order_detail.html', context)

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
    current_user = request.user
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
        "current_user": current_user
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

