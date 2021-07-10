import math, decimal, sys, logging, os
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError, transaction
from django.db.models import Max, Avg, Count, Q

from .forms import RegistrationForm, ChangePasswordForm, LoginForm
from .forms import CreateWatchForm, DeleteWatchForm, MakeABidForm, CloseBiddingForm
from .forms import PostCommentForm, CreateAListingForm, AddAddressForm, AmendAListingForm, AmendAddressForm
from .models import User, Category, Listings, Watchlist, Bids, Comments, Address
from django.utils import timezone

#Python logger, for logging error
logger = logging.getLogger(__name__)

def index(request):
    # This is the main entry function that will fetch and return list of item for display, including closed items.
    #
    # This  funtion will either get th list of all items, the list for a given category (cat),
    # the list for  a given user (usr) or for a give search (g).
    # If there are bids for a given item, it will fetch the highest bid startingprice for the item.
    #
    # The function will display 8 items per page and manages a paginatior.
    #
    # The user need no be logged it to access this function. But the query by user,
    # will return a error if the user is nt logged in.

    cat = request.GET.get('cat', None)
    usr = request.GET.get('usr', None)
    q   = request.GET.get('q', None)
    page = request.GET.get('page', 1)


    if cat is None and usr is None and q is None:
        heading = "Active Listings"
        list = Listings.objects.filter(publish=True).order_by('id')
    elif cat is not None:
        category = get_object_or_404(Category, pk=cat)
        heading = f"Listings for Category: { category }"
        list = Listings.objects.all().filter(categories=category.id).order_by('id')
    elif usr is not None:
        user = get_object_or_404(User, username=request.user)
        heading = f"Listing for User: { user.first_name } { user.last_name }"
        list = Listings.objects.all().filter(seller=user).order_by('id')
    elif q is not None:
        heading = f"Listing results for search: {q}"
        qs = Q(title__icontains=q)|Q(short_desc__icontains=q)|Q(details__icontains=q)
        list = Listings.objects.filter(qs).distinct().order_by('id')

    if len(list) > 0:
        for li in list:
            max_amt = li.bids.all().aggregate(Max('bidamt'))
            if max_amt['bidamt__max'] is not None:
                li.startingprice = decimal.Decimal(max_amt['bidamt__max']).quantize(decimal.Decimal('0.01'))


    paginator = Paginator(list, 8)
    try:
        listing = paginator.page(page)
    except PageNotAnInteger:
        listing = paginator.page(1)
    except EmptyPage:
        listing = paginator.page(paginator.num_pages)

    return render(request, "auctions/index.html", {
                                                    "listings": listing,
                                                    "heading": heading
                                                    })

@login_required
def create_a_listing(request):
    # This function creats a new listing. Only users who are signed in can access this function.
    #
    # The CreateAListingForm is presented to the user to create a item. The seller of
    # the item is set to be the user who is logged in. The publish time stamp is set
    # to now, if the publish flag is set to true.
    heading = "Create A Listing"
    context = {}
    initialise = {}
    msg = ""

    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        form = CreateAListingForm(request.POST)
        if 'submit' in request.POST:
            if form.is_valid():
                create_form = form.save(commit=False)
                create_form.seller = usr
                if form.cleaned_data.get('publish') == True:
                    create_form.publish_ts = timezone.now()
                categories = form.cleaned_data.get('categories')

                try:
                    # The save to listing and th category both must succed togather.
                    with transaction.atomic():
                        create_form.save()
                        for category in categories:
                            create_form.categories.add(category)
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "Failed to save Listing")
                else:
                    if form.cleaned_data.get('publish') == True:
                        messages.info(request, f"Your item titled, { form.cleaned_data.get('title') }, has been saved and published for bidding.")
                    else:
                        messages.info(request, f"Your item titled, { form.cleaned_data.get('title') } has been saved but not published.")

                return HttpResponseRedirect(request.session['return_url'])

            else:
                messages.error(request, "Please correct the highlighted error and resubmit.")
                context = { 'form': form,
                            'heading': heading}
                return render(request, "auctions/create_a_listing.html", context)
        else:
            # Request Cancelled
            messages.info(request, "Your item has not been saved.")
            return HttpResponseRedirect(request.session['return_url'])
    else:
        request.session['return_url'] = request.META.get('HTTP_REFERER', '/')
        initialise = {'seller': usr.id , 'publish_ts': False, 'closed': False}
        form = CreateAListingForm(initial=initialise)
        context = { 'form': form,
                    'heading': heading}
        return render(request, "auctions/create_a_listing.html", context)

@login_required
def amend_a_listing(request):
    # This function is for amending a listed item. It requires the ID of the item to amend.
    #
    # The user must be logged in to amend an item and the user must be the seller of the item.
    # The listing item is retrived, and the AmendAListingForm is instantiated with item details__icontains
    # and presented to the user for amendement.
    # If the publish flag is changed, the publish timestamp is updated to now before saving.

    heading = "Amend a Listing"
    context = {}
    return_url = '/'

    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        if 'submit' in request.POST:
            listing = get_object_or_404(Listings, pk=request.session['item'])
            form = AmendAListingForm(request.POST, instance=listing)
            if form.is_valid():
                publish_changed = False
                if form.has_changed() and 'publish' in form.changed_data:
                    publish_changed = True
                amend_form = form.save(commit=False)
                if publish_changed:
                    amend_form.publish_ts = timezone.now()
                try:
                    with transaction.atomic():
                        amend_form.save()
                        form.save_m2m()
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "Sorry, I could not save your update.")
                else:
                    messages.info(request, "Amendment saved.")
            else:
                messages.error(request, "Please correct the highlighted errors and resubmit.")
                context = { 'form': form, 'heading': heading }
                return render(request, "auctions/amend_a_listing.html", context )
        else:
            # Request cancelled
            messages.info(request, "Amendment was not saved.")
    else:
        request.session['return_url'] = request.META.get('HTTP_REFERER', '/')
        id = request.GET.get('id', None)
        if id is not None:
            try:
                listing = Listings.objects.get(pk=id)
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                messages.error(request, "I coundn't find the item you want to bid on!")
            else:
                #Ensure the user is the seller of the listing he/she want to amend
                if listing.seller.username == usr.username:
                    form = AmendAListingForm(instance=listing)
                    request.session['item'] = listing.id
                    request.session['initial_data'] = {'publish': listing.publish,
                                                        'closed': listing.closed}
                    context = { 'form': form, 'heading': heading }
                    return render(request, "auctions/amend_a_listing.html", context )
                else:
                    logger.error(f"User {usr.username} tried to amend item {listing.id}.")
                    messages.error(request, "I coundn't find the item you want to bid on!")
        else:
            logger.error(f"User {usr.username} tried to amend item with invalid listing id.")
            messages.error(request, "I coundn't find the item you want to bid on!")

    return HttpResponseRedirect(request.session['return_url'])

def view_a_listing(request):
    # This function gathers information for displying details of a n listing
    # and its associated comments.
    #
    # It needs the listing id as input, and will display different informations
    # if the user is logged in or not, and if the user is a seller of the listing.
    # Comments for the listing are retrived and displayed 4 comments a page.
    #
    heading = "Detail Listing"
    listing = None
    has_watch = False
    winning_bidder = None
    no_of_bids = 0
    no_of_ratings = 0
    star_rating = 0
    comments = None
    your_bid = 0
    startingprice = 0
    categories = []

    if request.user.is_authenticated:
        usr = get_object_or_404(User, username=request.user)
    else:
        usr=None

    id = request.GET.get('id')
    page = request.GET.get('page', 1)

    if id is not None:
        listing = get_object_or_404(Listings, pk=id)
        if listing is not None:
            no_of_bids = len(Bids.objects.filter(list_item=listing.id))
            # If rating is zero, assume no rating given, and not included in average calculatons.
            no_of_ratings = listing.item_comments.filter(rating__gt = 0).count()
            rating_avg = listing.item_comments.filter(rating__gt = 0).aggregate(Avg('rating'))
            if rating_avg['rating__avg'] is not None:
                star_rating = round(rating_avg['rating__avg'])

            max_amt = listing.bids.all().filter(withdrawn=False).aggregate(Max('bidamt'))
            if max_amt['bidamt__max'] is not None:
                startingprice = max_amt['bidamt__max']
                winning_bidder = Bids.objects.all().filter(bidamt=startingprice).filter(list_item=listing.id).get().bidder
            else:
                startingprice = listing.startingprice

            if request.user.is_authenticated:
                user_bid = listing.bids.all().filter(bidder=usr.id).aggregate(Max('bidamt'))
                if user_bid['bidamt__max'] is not None:
                    your_bid = user_bid['bidamt__max']

                if len(Watchlist.objects.all().filter(watcher=usr.id).filter(item=listing.id).filter(suspend_watch=False)) > 0:
                    has_watch = True

            for cat in listing.categories.all():
                categories.append((cat.id, cat.category),)
            print(f"Listng categories: {categories}")

            comments_list = listing.item_comments.all().order_by('comment_ts').reverse()
            paginator = Paginator(comments_list, 4)
            try:
                comments = paginator.page(page)
            except PageNotAnInteger:
                comments = paginator.page(1)
            except EmptyPage:
                comments = paginator.page(paginator.num_pages)

            context = { "listing": listing,
                        "comments": comments,
                        "heading": heading,
                        "has_watch": has_watch,
                        "winning_bidder": winning_bidder,
                        "no_of_ratings": no_of_ratings,
                        "no_of_bids": no_of_bids,
                        "star_rating": star_rating,
                        "your_bid": decimal.Decimal(your_bid).quantize(decimal.Decimal('.01')),
                        "startingprice": decimal.Decimal(startingprice).quantize(decimal.Decimal('.01')),
                        "categories": categories
                        }
            return render(request, "auctions/view_a_listing.html", context)
        else:
            messages.error(request, "I cannot find the listing.")
    else:
        messages.error(request, "I cannot find the listing.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def make_a_bid(request):
    # This function handles the placement of a bid.
    #
    # Only a user who is logged in cam make a bid. The listing must be published
    # and open for bidding. And the user cannot bid for his own item.
    #
    heading = "Make a Bid"
    max_bidamt = {}
    no_bids = False

    usr = get_object_or_404(User, username=request.user)

    if request.method == 'POST':
        form = MakeABidForm(request.POST, bidding_user=usr.id)
        if 'submit' in request.POST:
            if form.is_valid():
                bid_form = form.save(commit=False)
                bidamt = decimal.Decimal(form.cleaned_data['bidamt'])
                listing = get_object_or_404(Listings, pk=request.session['item'])
                max_bidamt = listing.bids.all().filter(withdrawn=False).aggregate(Max('bidamt'))
                if max_bidamt['bidamt__max'] is None:
                    max_bidamt['bidamt__max'] = listing.startingprice
                    no_bids = True
                if (no_bids == True and bidamt >= max_bidamt['bidamt__max']) or \
                    (no_bids == False and bidamt > max_bidamt['bidamt__max']):
                    bid_form.list_item = listing
                    bid_form.bidder = request.user
                    bid_form.bidamt = decimal.Decimal(bidamt)
                    bid_form.save()
                    messages.success(request, "Your bid has been recorded")
                    return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={request.session['item']}")
                else:
                    messages.error(request, "Your bid must be higher then the current bid!")
            else:
                print(form.errors)
                messages.error(request, "There has been an error on the form, please correct and resubmit.")
        else:
            messages.info(request, "No bids has been placed.")
            return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={request.session['item']}")

        context = { 'form': form,
                    'listing_title': request.session['listing_title'],
                    'heading': heading,
                    'max_bidamt': request.session['max_bidamt'] }
        return render(request, "auctions/make_a_bid.html", context )
    else:
        id = request.GET.get('id')
        if id is not None:
            try:
                listing = Listings.objects.get(pk=id)
            except Exception as e:
                messages.error(request, "Oh!, I coundn't find the item you want to bid on!")
            else:
                if not listing.closed and listing.publish == True:
                    if listing.seller.username != usr.username:
                        max_bidamt = listing.bids.all().filter(withdrawn=False).aggregate(Max('bidamt'))
                        if max_bidamt['bidamt__max'] is None:
                            max_bidamt['bidamt__max'] = listing.startingprice
                        request.session['item'] = id
                        request.session['max_bidamt'] = str(decimal.Decimal(max_bidamt['bidamt__max']).quantize(decimal.Decimal('.01')))
                        #initial the email field to the user email and the bidamount to the highest bid.
                        initialise = {'item_item': listing.id, 'notify_email': usr.email, 'bidamt': request.session['max_bidamt']}
                        # Pass the highest bid amount to the form, so the minimum on the form can be set. Pass the user Id,
                        # so that the selection for the addresses can be fitered to the user's addresses.
                        form = MakeABidForm(initial=initialise, max_bidamt=request.session['max_bidamt'], bidding_user=usr.id)

                        request.session['listing_title'] = listing.title
                        context = { 'form': form,
                                    'listing_title': listing.title,
                                    'heading': heading,
                                    'max_bidamt': request.session['max_bidamt'] }
                        return render(request, "auctions/make_a_bid.html", context )
                    else:
                        messages.error(request, "You cannot bid on your own listing. ")
                else:
                    messages.error(request, "You cannot bid on this item. It is either closed for biding, or not open fo biding ")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def close_bidding(request):
    # This function process a request to close bidding in a listing.
    #
    # The function needs the listing id of the listing to close the biddin on. the
    # function ensure only the seller can close the bidding. The seller can close
    # the bidding even if there are no bids. If there are o bids, the listing is
    # marked closed. If there are bis, the winning bid is also marked as accepted.
    heading = "Close Bidding"
    no_of_bids = 0
    max_bidamt = {}
    context = {}
    winningbid = None
    id = None
    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        id = request.session['item']
        try:
            listing = Listings.objects.get(pk=id)
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            messages.error(request, "I coundn't find the item you want to close bidding on!")
        else:
            if request.session['winningbid'] is not None:
                try:
                    winningbid = Bids.objects.get(pk=request.session['winningbid'])
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "I coundn't find the bid you want to was to accept!")
                else:
                    form = CloseBiddingForm(request.POST, instance=winningbid)
            else:
                winningbid = None
                form = CloseBiddingForm(request.POST)
            if 'submit' in request.POST:
                if form.is_valid():
                    closeform = form.save(commit=False)
                    listing.closed = True # Mark the listing as closed.
                    try:
                        with transaction.atomic():
                            listing.save()
                            if winningbid is not None:
                                closeform.bid_accepted = True # there is  winner, mark winner's bid as accepted.
                                closeform.save()
                                messages.success(request, f"The bidding for { listing.title } has been closed at { request.session['bidamt'] }")
                            else:
                                messages.warning(request, f"The bidding for { listing.title } has been closed. There was no winner!")
                    except IntegrityError:
                        messages.error("Sorry, I am not able to complete the transaction, a technical error has occured.")

                else:
                    logger.error(f'Form Error: {form.errors}')
                    messages.error(request, "Form Error. Please try again.")
            else:
                messages.info(request, "Cancelled: Returned without closing the bid.")

    else:
        id = request.GET.get('id')
        if id is not None:
            try:
                listing = Listings.objects.get(pk=id)
                no_of_bids = listing.bids.filter(withdrawn=False).count()
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                messages.error(request, "I coundn't find the item you want to close bidding on!")
            else:
                if listing.seller.id != usr.id:
                    messages.error(request, "You cannot close the bidding for this item!")
                else:
                    request.session['item'] = id
                    if no_of_bids == 0:
                        # Closing the bidding without an bids.
                        max_bidamt['bidamt__max'] = listing.startingprice
                        request.session['bidder'] = None
                        request.session['winningbid'] = None
                        winningbid = None
                    else:
                        try:
                            max_bidamt = listing.bids.filter(withdrawn=False).aggregate(Max('bidamt'))
                            winningbid = listing.bids.filter(withdrawn=False).filter(bidamt=max_bidamt['bidamt__max']).first()
                        except Exception as e:
                            logger.error(f"{type(e)} : {e}")
                            messages.error(request, "I coundn't find the highest bid!")
                            return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={id}")
                        else:
                            request.session['bidder'] = winningbid.bidder.id
                            request.session['winningbid'] = winningbid.id

                    request.session['bidamt'] = "{:.2f}".format(max_bidamt['bidamt__max'])
                    initialise = {"item_item": listing.id,
                                "bidder": request.session['bidder'],
                                "bidamt": max_bidamt['bidamt__max'],
                                "bid_accepted": True}

                    form = CloseBiddingForm(initial=initialise)

                    context = { 'form': form,
                                'listing_title': listing.title,
                                'heading': heading,
                                'max_bidamt': request.session['bidamt'] }
                    return render(request, "auctions/close_bidding.html", context)
        else:
            logger.error("A request to close a bidding with no listing item ID was made.")
            messages.error(request, "Oh, not sure how the request was made, no item was specified in the request!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={id}")

@login_required
def post_comment(request):
    # This function proces request to post a commnet on a listing.
    #
    # The function needs the listing id to record the commnet. The function
    # ensure only loged in users can post a comment. A user can post comments
    # on any listing item, including their own.
    heading = "Post a Comment"
    contect = {}
    id = None

    usr = get_object_or_404(User, username=request.user)

    if request.method == 'POST':
        form = PostCommentForm(request.POST)
        if 'submit' in request.POST:
            if form.is_valid():
                comment_form = form.save(commit=False)
                comment_form.commenting_user = request.user
                try:
                    comment_form.commenting_item = Listings.objects.get(pk=request.session['item'])
                    comment_form.save()
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "Sorry, I coundn't save your comment!")
                else:
                    messages.success(request, "Your comment has been saved.")
            else:
                messages.error(request, "Please correct the error and resubmit!")
                context = {'form': form, 'heading': heading}
                return render(request, "auctions/post_comment.html", context)
        else:
            messages.info(request, "Cancelled: Your comment has not been saved.")

        return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={request.session['item']}")
    else:
        id = request.GET.get('id')
        if id is not None:
            try:
                listing = Listings.objects.get(pk=id)
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                messages.error(request, "Sorry, I can't find a listing for this item to comment on!")
            else:
                initialise = {'commenting_item': listing.id, 'commenting_user': request.user }
                form = PostCommentForm(initial=initialise)
                request.session['item'] = id
                context = {'form': form, 'heading': heading, 'listing_title': listing.title}
                return render(request, "auctions/post_comment.html", context)
        else:
            logger.error("Invalid Get Request, id was not specified in the get request!")
            messages.error(request, "Sorry, There is no such item you can comment on!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def view_watchlist(request):
    # This functions retrives the list of watches for a user and displays 8 watches
    # per page, using a paginator. any watch is suspend state are filtered out.
    heading = "Your Watch List"
    list_page = request.GET.get('page', 1)
    context = {}
    try:
        usr = User.objects.get(username=request.user)
        list = Watchlist.objects.all().filter(watcher=usr.id).filter(suspend_watch=False).order_by('id')
    except Exception as e:
        logger.error(f"{type(e)} : {e}")
        messages.error(request, "Sorry, I am not able to retrive your watch list!")
    else:
        paginator = Paginator(list, 8)
        try:
            watchlist = paginator.page(list_page)
        except PageNotAnInteger:
            watchlist = paginator.page(1)
        except EmptyPage:
            watchlist = paginator.page(paginator.num_pages)

        context = {'watchlist': watchlist, 'heading': heading, 'count': paginator.count }
        return render(request, "auctions/view_watchlist.html", context)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_watch(request):
    # This function adds a watch entry given the listing ID.
    #
    # The user must be logged in to add a watch. A user cn add a watch on
    # any item, including his own.
    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        form = CreateWatchForm(request.POST)
        if 'submit' in request.POST:
            if form.is_valid():
                watch_form = form.save(commit=False)
                watch_form.watcher = request.user
                try:
                    watch_form.item = Listings.objects.get(pk=request.session['item'])
                    watch_form.save()
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "Sorry, I could't save your watch request.")
                else:
                    messages.success(request, "Saved: Your watch request has been saved!")
            else:
                messages.error(request, "Sorry, I am not able to save your watch request!")
        else:
            messages.info(request, "Cancelled: The watch request has not been saved.")

        return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={request.session['item']}")

    else:
        id = request.GET.get('id', None)
        if id is not None:
            try:
                listing = Listings.objects.get(pk=id)
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                messages.error(request, "Sorry, I can't find a listing for this item to add a watch!")
            else:
                request.session['item'] = id
                initialise = {'item': listing.id, 'watcher': request.user, 'notify_email': usr.email }
                form = CreateWatchForm(initial=initialise)

                context = { 'form': form, 'listing_title': listing.title }
                return render(request, "auctions/add_watch.html", context )
        else:
            logger.error("Invalid Get Request, id was not specified in the get request!")
            messages.error(request, "Sorry, I can't find a listing for this item!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_watch(request):
    # This functions removes a watch given the listing ID.
    #
    # The user must logged in and the user can only remove his watches.

    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        form = DeleteWatchForm(request.POST)
        if 'submit' in request.POST:
            if form.is_valid():
                watch_form = form.save(commit=False)
                watch_form.id = Watchlist.objects.get(pk=request.session['watch_id']).id
                try:
                    watch_form.delete()
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "Sorry, I am not able to remove your watch!!")

                else:
                    messages.success(request, "Removed: Your watch has been removed!")
            else:
                messages.error(request, "Sorry, I am not able to remove your watch!")
        else:
            messages.info(request, "Cancelled: The watch request has not been removed.")


        return HttpResponseRedirect(reverse("auctions:view_a_listing") + f"?id={request.session['item']}")
    else:
        id = request.GET.get('id')
        if id is not None:
            try:
                listing = Listings.objects.get(pk=id)
                watch_id = Watchlist.objects.all().filter(watcher=usr.id).filter(item=listing.id).filter(suspend_watch=False).first().id
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                messages.error(request, "Sorry, I can't find a listing for this item to remove a watch!")
            else:
                initialise = {'item': listing.id, 'watcher': request.user, 'notify_email': usr.email }
                form = DeleteWatchForm(initial=initialise)
                request.session['item'] = id
                request.session['watch_id'] = watch_id

                context = { 'form': form, 'listing_title': listing.title }
                return render(request, "auctions/remove_watch.html", context)
        else:
            logger.error("Invalid Get Request, id was not specified in the get request!")
            messages.error(request, "Sorry, I can't find a listing for this item to remove a watch!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def view_categories(request):
    # The function list all categories 8 items on a page.
    try:
        categories = Category.objects.order_by("id").all()
    except Exception as e:
        logger.error(f"{type(e)} : {e}")
        messages.error(request, "Sorry, I can't find any category!")
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        cat_page = request.GET.get('page', 1)

        paginator = Paginator(categories, 8)
        try:
            category = paginator.page(cat_page)
        except PageNotAnInteger:
            category = paginator.page(1)
        except EmptyPage:
            category = paginator.page(paginator.num_pages)

        return render(request, "auctions/category.html", {"category": category})


@login_required
def add_address(request):
    heading = "Add an Address"
    initialise = {}
    context = {}
    return_url = '/'

    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        form = AddAddressForm(request.POST)
        if 'cancel' not in request.POST:
            if form.is_valid():
                address_form = form.save(commit=False)
                address_form.username = usr
                try:
                    with transaction.atomic():
                        if form.cleaned_data.get('shipping_add') and form.cleaned_data.get('default_shipping'):
                            Address.objects.filter(username=usr).update(default_shipping=False)
                        if form.cleaned_data.get('billing_add') and form.cleaned_data.get('default_billing'):
                            Address.objects.filter(username=usr).update(default_billing=False)
                        address_form.save()
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                    messages.error(request, "Sorry, I could't save your your new address.")

                messages.success(request, "Addressed saved.")
            else:
                messages.error(request, "Please correct highlighted error and resubmit.")
                context = {'form': form, 'heading': heading}
                return render(request, "auctions/add_address.html", context )
        else:
            messages.info(request, "Address not saved!")

        return HttpResponseRedirect(request.session['return_url'])
    else:
        initialise = {'username': request.user }
        form = AddAddressForm(initial=initialise)

        request.session['return_url'] = request.META.get('HTTP_REFERER', '/')
        context = {'form': form, 'heading': heading}
        return render(request, "auctions/add_address.html", context )

@login_required
def list_address(request):
    heading ="Your List of Addresses"
    page = request.GET.get('page', 1)
    context = {}

    try:
        usr = User.objects.get(username=request.user)
        address_list = Address.objects.filter(username=usr).order_by('id')
    except Exception as e:
        logger.error(f"{type(e)} : {e}")
        messages.error(request, "Sorry, I am not able to retrive your address list!")
    else:
        paginator = Paginator(address_list, 8)
        try:
            addresses = paginator.page(page)
        except PageNotAnInteger:
            addresses = paginator.page(1)
        except EmptyPage:
            addresses = paginator.page(paginator.num_pages)

        context = {'addresses': addresses, 'heading': heading, 'count': paginator.count }
        return render(request, "auctions/list_address.html", context)

    return HttpResponseRedirect(request.session[request.META.get('HTTP_REFERER', '/')])

@login_required
def amend_address(request):
    heading = "Amend Address Details"
    context = {}
    return_url = '/'

    usr = get_object_or_404(User, username=request.user)

    if request.method == "POST":
        if 'cancel' not in request.POST:
            address = get_object_or_404(Address, pk=request.session["address_id"])
            form = AmendAddressForm(request.POST, instance=address)
            if form.is_valid():
                address_form = form.save(commit=False)
                address_form.username = usr
                if 'delete' not in request.POST:
                    try:
                        with transaction.atomic():
                            if form.cleaned_data.get('shipping_add') and form.cleaned_data.get('default_shipping'):
                                Address.objects.filter(username=usr).exclude(pk=request.session["address_id"]).update(default_shipping=False)
                            if form.cleaned_data.get('billing_add') and form.cleaned_data.get('default_billing'):
                                Address.objects.filter(username=usr).exclude(pk=request.session["address_id"]).update(default_billing=False)
                            address_form.save()
                    except Exception as e:
                        logger.error(f"{type(e)} : {e}")
                        messages.error(request, "Sorry, I could't save your your new address.")

                    messages.success(request, "Address amendment saved.")
                else:
                    try:
                        address.delete()
                    except Exception as e:
                        logger.error(f"{type(e)} : {e}")
                        messages.error(request, "Sorry, I couldn't delete the address.")
                    else:
                        messages.success(request, "Address deleted!")
            else:
                messages.error(request, "Oh!, Please correct the error and resubmit.")
                context = { 'form': form, 'heading': heading }
                return render(request, "auctions/amend_address.html", context)
        else:
            messages.info(request, "Addres Amendment canceled.")
    else:
        request.session['return_url'] = request.META.get('HTTP_REFERER', '/')
        id = request.GET.get('id', None)

        if id is not None:
            try:
                address = Address.objects.get(pk=id)
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                messages.error(request, "Oh!, I coundn't find the address you wanted to amend!")
            else:
                if address.username == request.user:
                    form = AmendAddressForm(instance=address)
                    request.session["address_id"] = id
                    context = { 'form': form, 'heading': heading }
                    return render(request, "auctions/amend_address.html", context)
                else:
                    logger.error(f"User {usr.username} tried to amend someone else's address, the address id was {id}.")
                    messages.error(request, "Oh!, I coundn't find the address you wanted to amend!")
        else:
            logger.error(f"User {usr.username} tried to amend an address with invalid address id.")
            messages.error(request, "Oh!, I coundn't find the address you wanted to amend!")



    return HttpResponseRedirect(request.session['return_url'])

@login_required
def view_my_account(request):
    heading="My Account"
    context = {}

    try:
        usr = User.objects.get(username=request.user)
    except Exception as e:
        logger.error(f"{type(e)} : {e}")
        messages.error(request, "Sorry, I am not able to retrive your account details!")
    else:
        context = {"account" : usr, "heading": heading}
        return render(request, "auctions/view_my_account.html", context)

    return HttpResponseRedirect(request.session[request.META.get('HTTP_REFERER', '/')])





#
# Misc functions
#
def pics(request, folder, picfile):
    picpath = "images/" + str(folder) + "/" + picfile
    context = {
        "folder" : folder,
        "picfile" : picfile,
        "picpath" : picpath
    }
    return render(request, "auctions/pics.html", context)

#
# Logins, Logouts, Register and Change Password.
#
def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in, Logout if your need to relogin again.")
        return HttpResponseRedirect(reverse("auctions:index"))

    if request.method == "POST":
        form = LoginForm(request.user, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                logger.info(f"User {user.id} logging in.")
                login(request, user)
                return HttpResponseRedirect(reverse("auctions:index"))
            else:
                return render(request, "auctions/login.html", {'form': form})
        else:
            return render(request, "auctions/login.html", {'form': form})
    else:
        form = LoginForm
        return render(request, "auctions/login.html", {'form': form})

@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed!")
            return redirect('auctions:index')
        else:
            messages.error(request, "Password change error, please see the error, and correct accordingly!")
    else:
        form = ChangePasswordForm(request.user)

    return render(request, "auctions/change_password.html", {'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            msg = f"You are registered. Your ID is {user.id}"
            messages.success(request, msg)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            messages.error(request, "Sorry, I am not able to register you!")
    else:
        form = RegistrationForm
    return render(request, "auctions/register.html", {"form": form })
