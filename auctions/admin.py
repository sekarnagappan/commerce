from django.contrib import admin
from .models import User, Address, Category, Listings, Bids, Comments, Watchlist


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email",
                    "is_active", "is_staff", "is_superuser",
                    "last_login", "date_joined"
                    )

class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "addresse_name",
                    "shipping_add", "default_shipping",
                    "billing_add", "default_billing",
                    "address","zipcode", "country", "update_ts"
                    )

class ListingsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "short_desc","seller",
                    "startingprice", "created_ts", "publish",
                    "publish_ts", "update_ts", "closed", "pic_url"
                    )
    filter_horizontal = ("categories",)

class BidsAdmin(admin.ModelAdmin):
    list_display = ( "id", "list_item", "bidder", "bidamt",
                    "bid_ts", "bid_accepted", "withdrawn",
                    "notify_email", "ship_to", "bill_to", "update_ts"
                    )

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "commenting_user", "commenting_item",
                    "comment_title", "rating", "comment_ts", "update_ts"
                    )
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "watcher", "watch_ts",
                    "suspend_watch","suspend_ts", "notify_email", "update_ts"
                    )
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "category_desc", "update_ts")

admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listings, ListingsAdmin)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
