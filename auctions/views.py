from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category
from .forms import NewListingForm, CommentForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all().exclude(active=False).order_by("title"),
        "heading": "All Active Listings:"
    })

def closedlistings(request):
        return render(request, "auctions/index.html", {
        "listings": Listing.objects.all().exclude(active=True).order_by("title"),
        "heading": "All Closed Listings:"
    })

def categories(request):
    cat_list = []
    for category in Category.objects.all():
        j = category.listings.filter(active=True).count()
        print(j)
        if j == 0:
            cat_list.append(category.id)
    print(cat_list)
    active_list = Category.objects.exclude(id__in=cat_list)

    return render(request, "auctions/categories.html", {
        "categories": active_list.order_by("title")
    })

def category(request, category_id):
    return render(request, "auctions/index.html", {
        "listings": Category.objects.get(id=category_id).listings.exclude(active=False),
        "heading": f"Category - {Category.objects.get(id=category_id).title}:"
    })

@login_required
def watchlist(request):
    return render(request, "auctions/index.html", {
        "listings": request.user.watchlist.all().order_by("title"),
        "heading": "Your Watchlist:"
    })

def listing(request, listing_id):

    user = request.user
    listing = Listing.objects.get(pk = listing_id)

    is_owner = True if str(listing.owner) == str(user.username) else False
   
    is_winner = True if listing.winner == user else False

    in_watchlist = False

    if user.is_authenticated:

        in_watchlist = True if listing_id in list(user.watchlist.values_list('id', flat=True)) else False
        
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                content = form.cleaned_data["comment"]
                comment = Comment(
                    user = user,
                    content = content,
                    listing = listing
                )
                comment.save()

            if "insert_watchlist" in request.POST:
                user.watchlist.add(listing_id)
            elif "delete_watchlist" in request.POST:
                user.watchlist.remove(listing_id)
            elif "bid" in request.POST:
                if int(request.POST["bid"]) > listing.current_price:
                    placed_bid = Bid(
                        user=user,
                        listing=Listing.objects.get(pk = listing_id),
                        bid= int(request.POST["bid"])
                    )
                    placed_bid.save()
                    listing.last_bidder=user
                    listing.current_price = int(request.POST["bid"])
                    listing.save()
                else:
                    return render(request, "auctions/error.html", {
                        "error_message": "Your bid is too low."
                    })
            elif "close_listing" in request.POST:
                listing.active = False
                listing.winner = listing.last_bidder
                listing.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(pk = listing_id),
        "in_watchlist": in_watchlist,
        "is_owner": is_owner,
        "commentform": CommentForm(),
        "comments": listing.listingcomments.order_by("-date"),
        "is_winner": is_winner
    })

@login_required
def createListing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            owner = request.user
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]

            cat = form.cleaned_data["category"]
            if cat in list(Category.objects.values_list('title', flat=True)):
                category = Category.objects.get(title=cat)
            else:
                category = Category(
                    title=cat
                )
                category.save()

            listing = Listing(
                owner=owner,
                title=title,
                description=description,
                starting_bid=starting_bid,
                image_url=image_url,
                cat=category,
                current_price=starting_bid)

            listing.save()
            category.listings.add(listing)

            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    return render(request, "auctions/create_listing.html", {
        "listingform": NewListingForm()
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
