from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comments, Bid

from datetime import datetime
from markdown2 import markdown

@login_required
def watch(request, listing_id):

    listing = Listing.objects.get(id = listing_id)
    watching = False
    try:
        watching = request.user in listing.watched_by.all()
    except:
        watching = False

    if(watching):
        listing.watched_by.remove(request.user)
    else:
        listing.watched_by.add(request.user)

    return HttpResponseRedirect(reverse("watchlist"))

@login_required
def watchlist(request):

    listings = request.user.watching.all()

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required
def close(request, listing_id):

    listing = Listing.objects.get(id = listing_id)
    listing.is_active=False

    if(listing.current_bid != -1): #bypassed if closing an auction without any bids
        winning_bid = listing.bid.latest("bid")
        listing.winner=winning_bid.bidder
        
    listing.save()

    return HttpResponseRedirect(reverse('listing', kwargs = {"listing_id": listing_id}))

@login_required
def bid(request, listing_id):

    b = int(request.POST["bid"])
    listing = Listing.objects.get(id = listing_id)
    #getting the maximum bid, also accessible by listing.current_bid
    try:
        max_bid = listing.bid.latest("bid").bid
    except:
        max_bid = -1

    if(b < listing.starting_bid):
        message = "Your bid is lower than the starting bid. [Try again](/listing/" + str(listing_id) + ")."
        return render(request, "auctions/error.html", {
            "message": markdown(message)
        })
    elif(b < max_bid and max_bid!=-1):
        message = "Your bid is lower than the current bid. [Try again](/listing/" + str(listing_id) + ")."
        return render(request, "auctions/error.html", {
            "message": markdown(message)
        })
    else:
        listing.current_bid = b
        listing.save()
        instance = Bid.objects.create(
            bid = b,
            bidder = request.user,
            listing = listing
        )
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

def categories(request):
    return render(request, "auctions/categories.html",{
        "categories": Category.objects.all()
    })

def category(request, category_id):
    req_cat = Category.objects.get(id = category_id)
    return render(request, "auctions/category.html",{
        "listings": req_cat.listings.filter(is_active=True),
        "category": req_cat.category_name
    })

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comments = listing.comments.all()

    try:
        watching = request.user in listing.watched_by.all()
    except:
        watching = False

    return render(request, "auctions/listing.html", {
        "item": listing,
        "comments": comments,
        "watching": watching
    })

def index(request):
    listings = Listing.objects.filter(is_active=True).all()
    
    return render(request, "auctions/index.html",{
        "listings": listings
    })

@login_required
def create(request):
    if request.method=='POST':

        try:
            instance = Listing.objects.create(
                title= request.POST["title"],
                description = request.POST["desc"],
                starting_bid = request.POST["bid"],
                img_url = request.POST["img_url"],
                category = Category.objects.get(pk=request.POST["category"]),
                owner = User.objects.get(id=request.user.id),
                is_active = True,
                current_bid = -1
            )
            return HttpResponseRedirect(reverse('listing', kwargs={"listing_id": instance.id}))
        except:
            return render(request, "auctions/error.html", {
                "message": "An error occurred while creating this listing. Please try again later."
            })

    return render(request, "auctions/create_listing.html",{
        "categories": Category.objects.all()
    })

@login_required
def comment(request, listing_id):
    if request.method=='POST':
        instance = Comments.objects.create(
            comment = request.POST["comment"],
            user = request.user,
            listing = Listing.objects.get(id = listing_id),
            date = datetime.now()
        )

        return HttpResponseRedirect(reverse('listing', kwargs={"listing_id": listing_id}))

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
