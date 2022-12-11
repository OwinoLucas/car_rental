from django.conf import settings
from django.urls import path
from django.contrib import admin
from django.urls import re_path as url
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', home, name = "home"),
    url(r'^admin_carlist/$', admin_car_list, name='adminIndex'),
    url(r'^listOrder/$', order_list, name = "order_list"),
    url(r'^(?P<id>\d+)/editOrder/$', order_update, name = "order_edit"),
    url(r'^(?P<id>\d+)/deleteOrder/$', order_delete, name = "order_delete"),
    url(r'^create/$', car_created, name = "car_create"),
    url(r'^message/$', admin_msg, name='message'),
    url(r'^(?P<id>\d+)/deletemsg/$', msg_delete, name = "msg_delete"),
    url(r'^login/', login_view, name='login'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^register/', register_view, name='register'),
    url(r'^carlist/$', car_list, name = "car_list"),
    url(r'^createOrder/$', order_created, name = "order_create"),
    url(r'^addCar/$', car_created, name = "add_car"),
    url(r'^(?P<id>\d+)/edit/$', car_update, name = "car_edit"),
    url(r'^profile/$', profile, name = "profile"),
    url(r'^(?P<id>\d+)/$', car_detail, name = "car_detail"),
    url(r'^detail/(?P<id>\d+)/$', order_detail, name = "order_detail"),
    url(r'^payment/(?P<id>\d+)/$', payment, name = "payment"),
    url(r'^(?P<id>\d+)/delete/$', car_delete, name = "car_delete"),

    url(r'^contact/$', contact, name = "contact"),

    url(r'^newcar/$', newcar, name = "newcar"),
    url(r'^(?P<id>\d+)/like/$', like_update, name = "like"),
    url(r'^popularcar/$', popular_car, name = "popularcar"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)