from django.urls import path
from .views import CreateStripeCheckoutSession, SuccessView, StripeWebhookView
from . import views

app_name = 'item'

urlpatterns = [
  path('', views.items, name='items'),
  path('new/', views.new, name='new'),
  path('<int:pk>/', views.detail, name='detail'),
  path('<int:pk>/edit/', views.edit, name='edit'),
  path('<int:pk>/delete/', views.delete, name='delete'),
  path("create-checkout-session/<int:pk>/", CreateStripeCheckoutSession.as_view(), name="create-checkout-session"),
  path("success/", SuccessView.as_view(), name="success"),
  path("webhooks/stripe/",StripeWebhookView.as_view(), name="stripe-webhook"),
]