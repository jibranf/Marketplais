import stripe
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Item
from django.contrib.auth.decorators import login_required
from .forms import NewItemForm, EditItemForm
from django.db.models import Q
from django.conf import settings
from django.views import View
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import  csrf_exempt

# stripe checkout page creation
stripe.api_key = settings.STRIPE_SECRET_KEY
class CreateStripeCheckoutSession(View):
    def post(self, request, *args, **kwargs):
        item = Item.objects.get(id=self.kwargs["pk"])

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount_decimal": float(item.price) * 100,
                        "product_data": {
                            "name": item.name,
                            "description": item.description,
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url = 'http://127.0.0.1:8000/items/success/',
            cancel_url = 'http://127.0.0.1:8000',
        )
        return redirect(checkout_session.url)

# viewing success page after transaction
class SuccessView(TemplateView):
    template_name = "item/success.html"

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle completed checkout session event
    """
    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            print("Payment successful")

        return HttpResponse(status=200)



def items(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    items = Item.objects.filter(sold=False)

    if category_id:
        items = items.filter(category_id=category_id)

    if query:
        items = items.filter(
            Q(name__icontains=query) | Q(description__icontains=query))

    return render(
        request, 'item/items.html', {
            'items': items,
            'query': query,
            'categories': categories,
            'category_id': int(category_id)
        })


def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    related_items = Item.objects.filter(category=item.category,
                                        sold=False).exclude(pk=pk)[0:3]

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items': related_items
    })


@login_required
def new(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.creator = request.user
            item.save()
            url = "/items/" + str(item.id)
            return redirect(url)
    else:
        form = NewItemForm()

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'New Item',
    })


@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, creator=request.user)
    item.delete()

    return redirect('dashboard:index')


@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, creator=request.user)

    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item:detail', pk=item.id)
    else:
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {
        'form': form,
        'title': 'Edit item',
    })
