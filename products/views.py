import requests

from django.shortcuts import render

from .models import Product

import re

from .scraper import scrape_books

from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout

from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required

from .models import Wishlist

from .models import PriceHistory

from .models import PriceAlert

from .models import Wishlist

from .models import RecentlyViewed

from rest_framework.response import Response

from rest_framework.decorators import api_view

from .serializers import (
    ProductSerializer,
    WishlistSerializer
)

from .serializers import (
    ProductSerializer,
    WishlistSerializer,
    PriceAlertSerializer
)

from .serializers import (

    ProductSerializer,

    WishlistSerializer,

    PriceAlertSerializer,

    PriceHistorySerializer

)

from .serializers import ProductSerializer

def normalize_title(title):

    title = title.lower()

    title = re.sub(r'([a-z])([0-9])', r'\1 \2', title)

    title = re.sub(r'([0-9])([a-z])', r'\1 \2', title)

    title = " ".join(title.split())

    return title

def home(request):

    product = request.GET.get("product")

    books = []

    sort = request.GET.get("sort")

    source = request.GET.get("source")

    min_price = request.GET.get("min_price")

    max_price = request.GET.get("max_price")

    products = []

    if product:

        # FIRST SEARCH DATABASE

        products = Product.objects.filter(
            title__icontains=product
        )

        # IF PRODUCTS NOT FOUND IN DATABASE

        if not products:

            # =========================
            # FETCH FROM FAKESTORE API
            # =========================

            response1 = requests.get(
                "https://fakestoreapi.com/products"
            )

            data1 = response1.json()

            for item in data1:

                search_text = normalize_title(product)

                title = normalize_title(item["title"])

                if search_text in title:

                    Product.objects.get_or_create(

                        title=item["title"],

                        source="FakeStore",

                        defaults={

                            "price": item["price"],

                            "category": item["category"],

                            "image": item["image"],

                            "rating": item["rating"]["rate"],

                            "description": item["description"]

                        }

                    )

            # =========================
            # FETCH FROM DUMMYJSON API
            # =========================

            response2 = requests.get(
                "https://dummyjson.com/products"
            )

            data2 = response2.json()["products"]

            for item in data2:

                search_text = normalize_title(product)

                title = normalize_title(item["title"])

                if search_text in title:

                    Product.objects.get_or_create(

                        title=item["title"],

                        source="DummyJSON",

                        defaults={

                            "price": item["price"],

                            "category": item["category"],

                            "image": item["thumbnail"],

                            "rating": item["rating"],

                            "description": item["description"],

                            "product_url": item["link"]

                        }

                    )

            # SEARCH AGAIN AFTER SAVING

            search_text = normalize_title(product)

            all_products = Product.objects.all()

            products = []

            for item in all_products:

                normalized_title = normalize_title(item.title)

                if search_text in normalized_title:

                    products.append(item)
    
    #Source Filtering Logic

    if source:

        filtered_products = []

        for item in products:

            if item.source == source:

                filtered_products.append(item)

        products = filtered_products
    
    #Filtering logic for min and max ranges 

    if min_price:

        products = [

            item for item in products

            if item.price >= float(min_price)

        ]


    if max_price:

        products = [

            item for item in products

            if item.price <= float(max_price)

        ]

    #Sorting Logic
    
    if sort == "low_to_high":

        products = sorted(
            products,
            key=lambda x: x.price
        )

    elif sort == "high_to_low":

        products = sorted(
            products,
            key=lambda x: x.price,
            reverse=True
        )

    elif sort == "rating":

        products = sorted(
            products,
            key=lambda x: x.rating,
            reverse=True
        )

    lowest_price = None

    if products:

        lowest_price = min(
            product.price for product in products
        )
    
    suggestions = Product.objects.all()[:20]

    
    if product:

        existing_products = Product.objects.filter(
            title__icontains=product
    )

    else:

        existing_products = Product.objects.none()
    
    
   # =========================
# BOOK SCRAPING
# =========================
    lowest_price = None

    if product:

        books = scrape_books(product)

        for item in books:

            price = item["price"].replace("£", "")

            obj, created = Product.objects.get_or_create(

                title=item["title"],

                source="BooksToScrape",

                defaults={

                    "price": float(price),

                    "category": "Books",

                    "image": item["image"],

                    "rating": 0,

                    "description": item["title"],

                    "product_url": item["link"]

                }

            )

            if not created:

                new_price = float(price)

                if obj.price != new_price:

                    old_price = obj.price

                    PriceHistory.objects.create(

                        product=obj,

                        price=new_price

                    )

                    if new_price < old_price:

                        wishlists = Wishlist.objects.filter(
                            product=obj
                        )

                        for wishlist in wishlists:

                            PriceAlert.objects.create(

                                user=wishlist.user,

                                product=obj,

                                old_price=old_price,

                                new_price=new_price

                            )

                    obj.price = new_price

                    obj.save()

                    print("UPDATED DB PRICE:", obj.price)

        # REFRESH PRODUCTS AFTER SCRAPING

        products = Product.objects.filter(
            title__icontains=product
        )


    if product:

        products = Product.objects.filter(
            title__icontains=product
        )

    else:

        products = []
    
    context = {

        "products": products,

        "searched": product,

        "lowest_price": lowest_price,

        "suggestions": suggestions,
    }

    

    return render(
        request,
        "products/home.html",
        context
    )


from django.shortcuts import get_object_or_404

def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    if request.user.is_authenticated:

        recent = RecentlyViewed.objects.filter(
        user=request.user,
        product=product
        )

        if recent.exists():

            recent.delete()

        RecentlyViewed.objects.create(

            user=request.user,

            product=product

        )

    context = {
        "product": product
    }

    return render(
        request,
        "products/detail.html",
        context
    )


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            return render(
                request,
                "products/register.html",
                {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("home")

    return render(
        request,
        "products/register.html"
    )

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect("home")

        return render(
            request,
            "products/login.html",
            {"error": "Invalid credentials"}
        )

    return render(
        request,
        "products/login.html"
    )


def user_logout(request):

    logout(request)

    return redirect("home")


@login_required
def add_to_wishlist(request, id):

    product = Product.objects.get(id=id)

    Wishlist.objects.get_or_create(

        user=request.user,

        product=product

    )

    return redirect(
        "product_detail",
        id=id
    )

@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    )

    context = {
        "wishlist_items": wishlist_items
    }

    return render(
        request,
        "products/wishlist.html",
        context
    )

@login_required
def remove_from_wishlist(request, id):

    wishlist_item = Wishlist.objects.get(
        id=id,
        user=request.user
    )

    wishlist_item.delete()

    return redirect("wishlist")

def price_history(request, id):

    product = Product.objects.get(id=id)

    history = PriceHistory.objects.filter(
        product=product
    ).order_by("-recorded_at")

    context = {

        "product": product,

        "history": history

    }

    return render(
        request,
        "products/price_history.html",
        context
    )

@login_required
def alerts(request):

    alerts = PriceAlert.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "products/alerts.html",
        {
            "alerts": alerts
        }
    )

@login_required
def dashboard(request):

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    alert_count = PriceAlert.objects.filter(
        user=request.user
    ).count()

    recent_alerts = PriceAlert.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    recent_products = RecentlyViewed.objects.filter(
    user=request.user
    ).order_by("-viewed_at")[:5]

    history_count = PriceHistory.objects.count()

    context = {

        "wishlist_count": wishlist_count,

        "alert_count": alert_count,

        "history_count": history_count,

        "recent_alerts": recent_alerts,

        "recent_products" : recent_products
    }

    return render(
        request,
        "products/dashboard.html",
        context
    )

@api_view(["GET"])
def product_api(request):

    search = request.GET.get("search")

    source = request.GET.get("source")

    products = Product.objects.all()

    if search:

        products = products.filter(
            title__icontains=search
        )
    
    if source:

        products = products.filter(
        source=source
    )

    serializer = ProductSerializer(
        products,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def product_detail_api(request, id):

    product = Product.objects.get(id=id)

    serializer = ProductSerializer(product)

    return Response(
        serializer.data
    )

@api_view(["GET"])
def wishlist_api(request):

    if not request.user.is_authenticated:

        return Response(
            {
                "error": "Login required"
            },
            status=401
        )

    wishlist = Wishlist.objects.filter(
        user=request.user
    )

    serializer = WishlistSerializer(
        wishlist,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def alerts_api(request):

    if not request.user.is_authenticated:

        return Response(
            {
                "error": "Login required"
            },
            status=401
        )

    alerts = PriceAlert.objects.filter(
        user=request.user
    ).order_by("-created_at")

    serializer = PriceAlertSerializer(
        alerts,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def history_api(request):

    history = PriceHistory.objects.all().order_by(
        "-recorded_at"
    )

    serializer = PriceHistorySerializer(
        history,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def product_history_api(request, id):

    product = Product.objects.get(id=id)

    history = PriceHistory.objects.filter(
        product_id=id
    ).order_by("-recorded_at")

    history_serializer = PriceHistorySerializer(
        history,
        many=True
    )

    return Response({

        "product": product.title,

        "current_price": product.price,

        "history": history_serializer.data

    })