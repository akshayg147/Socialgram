from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowerCount
from itertools import chain
import random
from django.http import HttpResponse
# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.all()
    #following
    user_following_list = []
    feed = []
    user_following = FollowerCount.objects.filter(follower = request.user.username)
    for users in user_following:
        user_following_list.append(users.user)
    for usernames in user_following_list:
        feed_list = Post.objects.filter(user=usernames)
        feed.append(feed_list)
    feed_list = list(chain(*feed))
    all_user = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    #suggestion
    new_suggestion_list = []
    for x in list(all_user):
        if x not in list(user_following_all):
            new_suggestion_list.append(x)
    curr_user  = User.objects.filter(username=request.user.username)
    final_suggestion_list = []
    for y in list(new_suggestion_list):
        if y not in list(curr_user):
            final_suggestion_list.append(y)
    random.shuffle(final_suggestion_list)
    username_profile = []
    username_profile_list = []
    for users in final_suggestion_list:
        username_profile.append(users.id)
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
    suggestion_username_profile_list = list(chain(*username_profile_list))
    return render(request, 'index.html',{'posts':feed_list,'user_profile':user_profile,'suggestion_username_profile_list':suggestion_username_profile_list[:4]})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username is taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log in and redirect to setting page
                user_login = auth.authenticate(username=username,password=password)
                auth.login(request, user_login)
                #create new profile for user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model,id_user= user_model.id)
                new_profile.save()
                return redirect('settings')

        else:
            messages.info(request,'PASSWORD DOES NOT MATCH')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('index')
        else:
            messages.info(request,'userid or password is wrong')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get('image') == None:
            image = user_profile.profileimage
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimage = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image'):
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimage = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')
    return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user,image=image,caption = caption)
        new_post.save()
        return redirect("index")
    else:
        return redirect("index")

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    #if i would've used get instead of filter it would have thrown me error as it is possible the object is not there in like-post
    #so to remove that error we used filter.
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_likes = post.no_likes+1
        post.save()
        return redirect('index')
    else:
        like_filter.delete()
        post.no_likes = post.no_likes-1
        post.save()
        return redirect('index')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_len = len(user_posts)
    follower = request.user.username
    user = pk
    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
    user_follower = len(FollowerCount.objects.filter(user=pk))
    user_following = len(FollowerCount.objects.filter(follower=pk))
    context = {
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'user_post_len':user_post_len,
        'button_text':button_text,
        'user_follower':user_follower,
        'user_following':user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('index')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains= username)

        username_profile = []
        username_profile_list = []
        for user in username_object:
            username_profile.append(user.id)
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html',{'user_profile':user_profile, 'username_profile_list':username_profile_list})