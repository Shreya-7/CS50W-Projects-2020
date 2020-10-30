from django.contrib import admin

from .models import Category, Listing, Bid, Comments

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comments)
