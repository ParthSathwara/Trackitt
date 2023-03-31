from django.shortcuts import render, HttpResponse, redirect
from yahoo_fin.stock_info import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import time
from threading import Thread
import queue
from asgiref.sync import sync_to_async


def home(request):
    if request.user.is_authenticated:
        return redirect('picker')
    else:
        return render(request, 'home.html')

@login_required
def stock_picker(request):
    stk_pikr = tickers_nifty50()
    print(stk_pikr)
    return render(request, 'picker.html', {'context': stk_pikr})

@login_required
def stock_tracker(request):
    start = time.time()
    selected_stocks = request.GET.getlist('stockpicker')
    stockshare=str(selected_stocks)[1:-1]
    data = {}
    all_stocks = tickers_nifty50()
    for i in selected_stocks:
        if i in all_stocks:
            pass
        else:
            return HttpResponse('ERROR')
        
    n_threads = len(selected_stocks)
    thread_list = []
    que = queue.Queue()
    for i in range(n_threads):
        thread = Thread(target=lambda q, arg1:q.put({selected_stocks[i]: get_quote_table(arg1)}) , args=(que, selected_stocks[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)

        
    end = time.time()
    time_taken = end - start
    print('###############DATA################')
    print(data)
    print('>>>> TIME TAKEN: ', time_taken)    
    return render(request, 'tracker.html', {'context': data, 'room_name':'track', 'selectedstock':stockshare})

def handleSignup(request):
    if request.method == "POST":
        # Get the post parameters
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # Checksum of all thr provided fields
        if len(username) > 10 or len(username) < 3:
            messages.error(request, 'User name must be beween 3 to 10 characters')
            return redirect('home')

        if not username.isalnum() :
            messages.error(request, 'User name must not contain any special characters')
            return redirect('home')

        if pass1 != pass2:
            messages.error(request, 'Passwords do not match')
            return redirect('home')

        # creating user 
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, 'User account successfully created!!!, Please login to your new account ')
        return redirect('home')

    else:
        return HttpResponse('404 Not found')

def handleLogin(request):
    if request.method == "POST":
        loginusername = request.POST['loginusername']
        loginpass = request.POST['loginpass']
        user = authenticate(username=loginusername, password=loginpass)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('picker')
        else:
            messages.error(request, 'Invalid credentials!!! Please Try again')
            return redirect('home')
        
    messages.warning(request, 'Login for access')
    return redirect('home')

def handleLogout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('home')