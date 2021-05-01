from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator

from .models import User, Post
from .util import login_required_handler, misc_error_handler, request_not_put_handler

from datetime import datetime
import json


@login_required_handler
@misc_error_handler
# view to create a new post
def new_post(request):

    created_post = Post.objects.create(
        content=request.POST['content'],
        timestamp=datetime.now(),
        poster=request.user
    )
    return redirect(reverse('index'))


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        'posts': page_obj
    })


@login_required_handler
@misc_error_handler
# view to return liked posts
def liked(request):

    posts = User.objects.get(
        username=request.user.username).likes.all().order_by('-timestamp')

    # pagination
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        'posts': page_obj,
        'liked': True
    })


@login_required_handler
@misc_error_handler
def profile(request, username):

    user = User.objects.get(username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        'posts': page_obj,
        'user_profile': user,
        'following': username in [person.username for person in User.objects.get(username=request.user.username).following.all()]
    })


@login_required_handler
@misc_error_handler
def following(request):

    follows = User.objects.get(username=request.user.username).following.all()
    posts = []

    for person in follows:
        posts.extend(User.objects.get(username=person.username).posts.all())

    posts.sort(reverse=True, key=lambda x: x.timestamp)

    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        'posts': page_obj,
        'following': True
    })


@csrf_exempt
@login_required_handler
@misc_error_handler
@request_not_put_handler
def follow(request, username):

    person_to_follow = User.objects.get(username=username)
    logged_in_user = User.objects.get(username=request.user.username)
    following = False
    try:
        following = username in [person.username for person in User.objects.get(
            username=request.user.username).following.all()]
    except:
        following = False

    if(following):
        person_to_follow.followers.remove(request.user)
        person_to_follow.follower_count -= 1
        logged_in_user.following_count -= 1

    else:
        person_to_follow.followers.add(request.user)
        person_to_follow.follower_count += 1
        logged_in_user.following_count += 1

    person_to_follow.save()
    logged_in_user.save()

    return JsonResponse({
        'followed': ['Follow', 'Unfollow'][not following],
        'followers': person_to_follow.follower_count,
        'following': person_to_follow.following_count
    }, status=200)


@csrf_exempt
@login_required_handler
@misc_error_handler
@request_not_put_handler
def like(request, post_id):

    post = Post.objects.get(id=post_id)
    liked = False
    try:
        liked = request.user in post.likers.all()
    except:
        liked = False

    if(liked):
        post.likers.remove(request.user)
        post.likes -= 1

    else:
        post.likers.add(request.user)
        post.likes += 1

    post.save()

    return JsonResponse({
        'likes': post.likes,
        'liked': ['Like', 'Unlike'][not liked]
    }, status=200)


@csrf_exempt
@login_required_handler
@misc_error_handler
def edit_post(request, post_id):

    if request.method == 'POST':

        post = Post.objects.get(id=post_id)

        content = json.loads(request.body).get('content', 'no')

        post.content = content
        post.timestamp = timezone.now()
        post.save()
        return JsonResponse({
            'content': post.content,
            'timestamp': post.timestamp
        }, status=200)

    else:
        return render(request, "network/error.html", {
            'message': 'You cannot edit this post.'
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
