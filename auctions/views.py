from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import (
    Textarea, HiddenInput, NumberInput,
    ModelForm, Select, TextInput, ValidationError)
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Bid, Comment, Listing, User


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['user', 'category', 'title', 'description', 'price']
        # Hide the 'user' input, which will be autofilled
        labels = {
            'user': ''
        }
        widgets = {
            'user': HiddenInput(),
            'title': TextInput(attrs={
                'style': 'width: 300px;'
            }),
            'description': Textarea(attrs={
                'style': 'width: 300px;'
            }),
            'category': Select(attrs={
                'style': 'width: 300px;'
            }),
            'price': NumberInput(attrs={
                'placeholder': '$0.00',
                'style': 'width: 300px;'
            })
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["value"]
        labels = {
            'value': ''
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        labels = {
            'content': ''
        }


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def listing_view(request, listing_id):
    form = BidForm()
    comment_form = CommentForm()
    if request.method == 'GET':
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            raise Http404("Listing not found.")
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": form,
                "comment_form": comment_form
            })

    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        user = request.user
        if user.is_authenticated:
            if request.POST.get("watch"):
                if user in listing.watchers.all():
                    listing.watchers.remove(user)
                    messages.success(request, 'Removed from watchlist')
                else:
                    listing.watchers.add(user)
                    messages.success(request, 'Added to watchlist')

            if request.POST.get("close"):
                listing.open = False
                listing.save()
        else:
            messages.error(request, "You must be logged in.")

        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))


def bid_view(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        if request.user.is_authenticated:
            bid = Bid(user=request.user, listing=listing)
            form = BidForm(request.POST, instance=bid)
            if form.is_valid():
                if request.user == listing.user:
                    form.add_error(
                        'value', "You can't bid on your own listing")
                elif listing.bids.count() > 0:
                    if request.user == listing.bids.last().user:
                        form.add_error(
                            'value', "You are already the winning bidder")
                    elif form.cleaned_data['value'] \
                        <= listing.bids.last().value:
                        form.add_error('value', ValidationError(
                            "You must bid higher than the winning bid"))
                elif form.cleaned_data['value'] < listing.price:
                    form.add_error('value', ValidationError(
                        "You must bid at least as much as the starting price"))
                else:
                    form.save()
                    listing.price = form.cleaned_data['value']
                    listing.save()
                    messages.success(request, "Bid successful!")
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "form": form
            })
        else:
            messages.error(request, "You must be logged in to bid.")
            return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
    else:
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))


@login_required
def comment_view(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        comment = Comment(user=request.user, listing=listing)
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment posted")
    return HttpResponseRedirect(reverse('listing', args=(listing.id,)))


@login_required
def watchlist_view(request):
    return render(request, "auctions/watchlist.html")


def categories_view(request):
    categories = Listing.category.field.choices
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def browse_view(request, category):
    listings = Listing.objects.filter(category=category, open=True)
    return render(request, "auctions/browse.html", {
        "listings": listings
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


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/create.html", {
            'form': form
        })

    else:
        # Create the empty form, and pre-fill the 'user'
        # input with the current user
        form = ListingForm(initial={'user': request.user})
        return render(request, "auctions/create.html", {
            'form': form
        })
