from django.shortcuts import render, redirect
from .forms import SignupForm
from item.models import Category, Item
from django.contrib.auth import logout

def index(request):
    items = Item.objects.filter(sold=False)[0:6]
    categories = Category.objects.all()

    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items,
    })

def contact(request):
    return render(request, 'core/contact.html')

def signup(request):
  form = SignupForm()
  if request.method == 'POST':
    form = SignupForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('/login/')
    
  return render(request, 'core/signup.html', {'form': form})

def logout_view(request):
  logout(request)
  redirect(request)
  