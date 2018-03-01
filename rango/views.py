from django.shortcuts import render
from rango.models import Category, Page
import pdb;
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
  request.session.set_test_cookie()
  context = RequestContext(request)
  category_list = Category.objects.order_by('-likes')[:5]
  context_dict = {'categories': category_list}

  if request.session.get('last_visit'):
      last_visit_time = request.session.get('last_visit')
      visits = request.session.get('visits', 0)

      if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
          request.session['visits'] = visits + 1
          request.session['last_visit'] = str(datetime.now())
  else:
      request.session['last_visit'] = str(datetime.now())
      request.session['visits'] = 1

  return render_to_response('rango/index.html', context_dict, context)

def about(HttpRequest):
  context_dict = {}
  context_dict['visit_count'] = HttpRequest.session.get('visits')

  return render(HttpRequest, 'rango/about.html', context_dict)

def category(HttpRequest, category_name_slug):
  context_dict = {}

  try:
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category_name'] = category.name
    pages = Page.objects.filter(category=category)
    context_dict['pages'] = pages
    context_dict['category'] = category
    context_dict['category_name_slug'] = category_name_slug
  except Category.DoesNotExist:
    pass
  return render(HttpRequest, 'rango/category.html', context_dict)

def add_category(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)

    if form.is_valid():
      cat = form.save(commit=True)
      print cat, cat.slug
      return index(request)
    else:
      print form.errors
  else:
    form = CategoryForm()

  return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
  try:
    cat = Category.objects.get(slug=category_name_slug)
  except Category.DoesNotExist:
    cat = None

  if request.method == 'POST':
    form = PageForm(request.POST)
    if form.is_valid():
      if cat:
        page = form.save(commit=False)
        page.category = cat
        page.views = 0
        page.save()

        return category(request, category_name_slug)
    else:
      print form.errors
  else:
    form = PageForm()

  context_dict = {'form': form, 'category': cat}
  return render(request, 'rango/add_page.html', context_dict)

def register(request):
    if request.session.test_cookie_worked():
      print ">>>> TEST COOKIE WORKED!"
      request.session.delete_test_cookie()

    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
              login(request, user)
              return HttpResponseRedirect('/rango/')
            else:
              return HttpResponse("Your Rango account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html', {})

#decorator
@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')
