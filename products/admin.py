from django.contrib import admin
from .models import Product

admin.site.register(Product)

from .models import Wishlist

admin.site.register(Wishlist)

from .models import PriceHistory

admin.site.register(PriceHistory)

from .models import PriceAlert

admin.site.register(PriceAlert)

from .models import RecentlyViewed

admin.site.register(RecentlyViewed)