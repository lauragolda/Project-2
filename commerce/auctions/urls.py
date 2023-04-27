from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createListing, name="create"),
    path("displayCategory", views.display, name="displayCategory"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("removeWL/<int:id>", views.remove, name="removeWL"),
    path("addWL/<int:id>", views.add, name="addWL"),
    path("watchlist", views.displayWL, name="watchlist"),
    path("addcomment/<int:id>", views.addComment, name="addcomment"),
    path("addbid/<int:id>", views.addBid, name="addbid"),
    path("closeauction/<int:id>", views.closeAuction, name="closeauction")
]