from django.urls import path
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import RedirectView

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("change_password", views.change_password, name="change_password"),
    path("create_a_listing", views.create_a_listing, name="create_a_listing"),
    path("view_a_listing", views.view_a_listing, name="view_a_listing"),
    path("amend_a_listing", views.amend_a_listing, name="amend_a_listing"),
    path("make_a_bid", views.make_a_bid, name="make_a_bid"),
    path("close_bidding", views.close_bidding, name="close_bidding"),
    path("post_comment", views.post_comment, name="post_comment"),
    path("view_watchlist", views.view_watchlist, name="view_watchlist"),
    path("add_watch", views.add_watch, name="add_watch"),
    path("remove_watch", views.remove_watch, name="remove_watch"),
    path("view_categories", views.view_categories, name="view_categories"),
    path("list_by_category", views.index, name="list_by_category"),
    path("add_address", views.add_address, name='add_address'),
    path("amend_address", views.amend_address, name="amend_address"),
    path("list_address", views.list_address, name='list_address'),
    path("view_my_account", views.view_my_account, name='view_my_account'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/auctions/images/favicon.ico')),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
