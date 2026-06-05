from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("wishlist/add/<int:id>/",views.add_to_wishlist,name="add_to_wishlist"),
    path("wishlist/",views.wishlist,name="wishlist"),
    path("wishlist/remove/<int:id>/",views.remove_from_wishlist,name="remove_from_wishlist"),
    path("price-history/<int:id>/",views.price_history,name="price_history"),
    path("alerts/",views.alerts,name="alerts"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("api/products/",views.product_api,name="product_api"),
    path("api/products/<int:id>/",views.product_detail_api,name="product_detail_api"),
    path("api/wishlist/",views.wishlist_api,name="wishlist_api"),
    path("api/alerts/",views.alerts_api,name="alerts_api"),
    path("api/price-history/",views.history_api,name="history_api"),
    path("api/price-history/<int:id>/",views.product_history_api,name="product_history_api"),
]
