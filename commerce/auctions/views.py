from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


def index(request):
    activeListings = Listing.objects.filter(active=True)
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": categories
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def createListing(request):
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageURL = request.POST["imageURL"]
        price = request.POST["price"]
        category = request.POST["category"]

        user = request.user

        categoryData = Category.objects.get(name=category)

        bid = Bid(bid=int(price), user=user)
        bid.save()
        listing = Listing(
            title=title,
            description=description,
            imageURL=imageURL,
            price=bid,
            category=categoryData,
            owner=user
        )

        listing.save()

        return HttpResponseRedirect(reverse(index))
    

def display(request):
    if request.method == "POST":
        categoryForm = request.POST["category"]
        category = Category.objects.get(name=categoryForm)
        activeListings = Listing.objects.filter(active=True, category=category)
        categories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": categories
        })
    

def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchList = request.user in listingData.watchList.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchList": isListingInWatchList,
        "comments": allComments,
        "isOwner": isOwner
    })

def remove(request, id):
    listingData = Listing.objects.get(pk=id)
    user = request.user
    listingData.watchList.remove(user)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def add(request, id):
    listingData = Listing.objects.get(pk=id)
    user = request.user
    listingData.watchList.add(user)
    return HttpResponseRedirect(reverse("listing",args=(id, )))

def displayWL(request):
    user = request.user
    listings = user.watchList.all()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

def addComment(request, id):
    user = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]

    newComment = Comment(
        author = user,
        listing = listingData,
        message=message
    )

    newComment.save()

    return HttpResponseRedirect(reverse("listing",args=(id, )))


def addBid(request, id):
    newBid = request.POST['newbid']
    listingData = Listing.objects.get(pk=id)
    isListingInWatchList = request.user in listingData.watchList.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    if int(newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()

        return render(request, "auctions/listing.html",{
            "listing":listingData,
            "message":"Bid was successfully updated",
            "update": True,
            "isListingInWatchList": isListingInWatchList,
            "comments": allComments,
            "isOwner": isOwner
        })
    else:
        return render(request, "auctions/listing.html",{
            "listing":listingData,
            "message":"Bid wasn't updated, your bid needs to be greater than the current price",
            "update": False,
            "isListingInWatchList": isListingInWatchList,
            "comments": allComments,
            "isOwner": isOwner
        })
    
def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    isOwner = request.user.username == listingData.owner.username
    isListingInWatchList = request.user in listingData.watchList.all()
    allComments = Comment.objects.filter(listing=listingData)
    listingData.active = False
    listingData.save()
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchList": isListingInWatchList,
        "comments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Auction is Closed!"
    })



