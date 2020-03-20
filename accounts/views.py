from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect
from .forms import SignUpForm

##########################
##### Accounts Views #####
##########################

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('main-home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
