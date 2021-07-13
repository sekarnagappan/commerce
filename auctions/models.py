from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    pass
#    def __str__(self):
#        return f'{self.first_name} {self.last_name}'

class Address(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="address", related_query_name="address", verbose_name='User')
    addresse_name = models.CharField(max_length=64, verbose_name='Addresse')
    address = models.TextField()
    zipcode = models.CharField(blank=True, max_length=10, verbose_name='Zip Code')
    country = models.CharField(max_length=64, verbose_name='Country')
    shipping_add = models.BooleanField(default=False, help_text="Can this address be used as a shipping?", verbose_name='Shipping?')
    billing_add = models.BooleanField(default=False, help_text="Can this addresed used as a billing address?",verbose_name='Billing?')
    default_shipping = models.BooleanField(default=False, help_text="Is this the default shipping address?",verbose_name='Default Ship?')
    default_billing = models.BooleanField(default=False, help_text="Is this the default billing address?",verbose_name='Default Bill?')
    update_ts = models.DateTimeField(auto_now=True, verbose_name="Update Timestamp")

    def __str__(self):
        return( f"Addresse: {self.addresse_name}")


class Category(models.Model):
    category = models.CharField(max_length=64,unique=True)
    category_desc = models.TextField()
    update_ts = models.DateTimeField(auto_now=True, verbose_name="Update Timestamp")

    def __str__(self):
        return(f'{self.category}')

class Listings(models.Model):
    title = models.CharField(max_length=64, verbose_name="Listing Title",unique=True)
    short_desc = models.CharField(max_length=128, help_text="Short Description", verbose_name="Short Desc")
    details = models.TextField(help_text="Details", verbose_name="Details")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userlistings", related_query_name="userlistings")
    startingprice = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Startng bid price.", verbose_name="Starting Price")
    created_ts = models.DateTimeField(auto_now_add=True, verbose_name="Creation Timestamp")
    publish = models.BooleanField(default=False, help_text="Select to publish")
    publish_ts = models.DateTimeField(blank=True, null=True, verbose_name="Publish Timestamp")
    closed = models.BooleanField(default=False, help_text="Close to accept highest bid.", verbose_name="Bidding Closed")
    categories = models.ManyToManyField(Category, blank=True, related_name="listings", related_query_name="listings")
    pic_url = models.URLField(max_length=200, default= "http://127.0.0.1:8800/media/images/blank.jpg", help_text="Provide URL of where your pictures are.", verbose_name="Picture URL")
    pic_upload = models.ImageField(upload_to='images/', default= "http://127.0.0.1:8800/media/images/blank.jpg", help_text="Select a picture (*.jpg, *.gif, *.png) to upload", verbose_name="Upload Picture")
    update_ts = models.DateTimeField(auto_now=True, verbose_name="Update Timestamp")

    class Meta():
        indexes = [
            models.Index(fields=['title'], name='title.idx'),
            models.Index(fields=['title', 'seller'], name='title_seller.idx')
        ]

    def __str__(self):
        status = "Closed" if self.closed else "Published" if self.publish else "Draft"
        return (f'{self.title}: "{self.short_desc}" ({status})')

class Bids(models.Model):
    list_item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids", related_query_name="bids", verbose_name="List Item")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="biddings", related_query_name="biddings", verbose_name="Bidding User")
    bidamt = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="What is your bid? Must be higher then the highest bid.", verbose_name="Bib Price")
    bid_ts = models.DateTimeField(auto_now_add=True, verbose_name="Bid Timestamp")
    bid_accepted = models.BooleanField(default=False, help_text="This bid is accepted and bidding will close.", verbose_name="Bid Accpeted")
    withdrawn = models.BooleanField(default=False, help_text="To withdraw your bid.", verbose_name="Withdrawan")
    notify_email = models.EmailField(blank=True, max_length=254, help_text="Email to notify win, if not provided, default profile email will be used.", verbose_name="Nofitcation Email")
    ship_to = models.ForeignKey(Address, null=True, on_delete=models.PROTECT, related_name='shippings', related_query_name='shippings', verbose_name="Ship To")
    bill_to =models.ForeignKey(Address, null=True, on_delete=models.PROTECT, related_name='billings', related_query_name='billings', verbose_name="Bill To")
    update_ts = models.DateTimeField(auto_now=True, verbose_name="Update Timestamp")
    def __str__(self):
        status = "Active" if not (self.bid_accepted and self.withdrawn) else "Closed"
        return(f'Item: {self.list_item} Bidder: {self.bidder} Amt: {self.bidamt} Status:{status}')


class Comments(models.Model):
    commenting_user = models.ForeignKey(User, null=True,on_delete=models.SET_NULL, related_name="comments", related_query_name="comments", verbose_name="User")
    commenting_item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="item_comments", related_query_name="item_comments", verbose_name="List Item")
    comment_title = models.CharField(max_length=64, help_text="Give a title to your comment.", verbose_name="Coment Title")
    comment = models.TextField(help_text="Please enter your comments here.", verbose_name="Comment")
    rating =  models.PositiveSmallIntegerField(default=0, help_text="Rate the Item, 1 to 5 stars.", verbose_name="ratings", validators=[MinValueValidator(0),MaxValueValidator(5)])
    comment_ts = models.DateTimeField(auto_now_add=True, verbose_name="Comment Timestamp")
    update_ts = models.DateTimeField(auto_now=True, verbose_name="Update Timestamp")

    def __str__(self):
        return (f'User :{self.commenting_user} List Item :{self.commenting_item} Title :{self.comment_title}')

class Watchlist(models.Model):
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="watchlist", related_query_name="watchlist", verbose_name="Watch Item")
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchings", related_query_name="watchings", verbose_name="Watcher")
    watch_ts = models.DateTimeField(auto_now_add=True, verbose_name="Watch Created Time")
    suspend_watch = models.BooleanField(default=False, verbose_name="Suspend Watch")
    suspend_ts = models.DateTimeField(blank=True, null=True, verbose_name="Suspend Time")
    notify_email = models.EmailField(blank=True, max_length=254, help_text="Email to notify changes", verbose_name="Notify Email")
    update_ts = models.DateTimeField(auto_now=True, verbose_name="Update Timestamp")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item', 'watcher', 'suspend_ts'], name="item-watcher")
        ]
