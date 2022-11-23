from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing_view, name="listing"),
    path("listing/bid/<int:listing_id>", views.bid_view, name="bid"),
    path("listing/comment/<int:listing_id>", views.comment_view, name="comment"),
    path("categories", views.categories_view, name="categories"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("categories/<str:category>", views.browse_view, name="browse"),
]
