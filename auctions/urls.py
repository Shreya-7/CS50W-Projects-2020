from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watch/<int:listing_id>", views.watch, name="watch")
]
