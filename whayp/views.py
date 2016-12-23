import uuid

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from .forms import PostForm, UserForm
from .models import Post, Photo

EXT = '.jpg'

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def create_post(request):
    if not request.user.is_authenticated():
        return render(request, 'whayp/login.html')
    else:
        form = PostForm(request.POST)
        if request.POST:
            post = form.save(commit=False)
            file_list = request.FILES.getlist("myfiles")
            if form.is_valid():
                for tmp in filter(lambda w: w.name.split('.')[-1] not in IMAGE_FILE_TYPES, file_list):
                    return render(request, 'whayp/create_post.html', {
                        'post': post,
                        'form': form,
                        'error_message': 'Image file must be PNG, JPG, or JPEG',
                    })
                post.user = request.user
                post.save()
                for count, file in enumerate(file_list):
                    file_name = str(uuid.uuid4())
                    photo = Photo()
                    photo.post = post
                    file.name = file_name + EXT
                    photo.photo_file = file
                    photo.save()
                return render(request, 'whayp/detail.html', {'post': post})
            else:
                return render(request, 'whayp/create_post.html', {
                    "form": form,
                    'error_message': 'Add image, please',
                })
        return render(request, 'whayp/create_post.html', {
            "form": form,
        })


def process(file, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def delete_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    post.delete()
    posts = Post.objects.filter(user=request.user)
    return render(request, 'whayp/index.html', {'posts': posts})


def detail(request, post_id):
    if not request.user.is_authenticated():
        return render(request, 'whayp/login.html')
    else:
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        return render(request, 'whayp/detail.html', {'post': post, 'user': user})


def favorite(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    try:
        photo.is_favorite = not photo.is_favorite
        photo.save()
    except (KeyError, Photo.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    try:
        post.is_favorite = not post.is_favorite
        for ph in post.photo_set.all():
            ph.is_favorite = True
            ph.save()
        post.save()
    except (KeyError, Post.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'whayp/login.html')
    else:
        posts = Post.objects.filter(user=request.user)
        photo_results = Photo.objects.all()
        query = request.GET.get("q")
        if query:
            posts = posts.filter(
                Q(post_title__icontains=query) |
                Q(artist__icontains=query)
            ).distinct()
            photo_results = photo_results.filter(
                Q(photo_title__icontains=query)
            ).distinct()
            return render(request, 'whayp/index.html', {
                'posts': posts,
                'photos': photo_results,
            })
        else:
            return render(request, 'whayp/index.html', {'posts': posts})


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'whayp/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                posts = Post.objects.filter(user=request.user)
                return render(request, 'whayp/index.html', {'posts': posts})
            else:
                return render(request, 'whayp/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'whayp/login.html', {'error_message': 'Invalid login'})
    return render(request, 'whayp/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                posts = Post.objects.filter(user=request.user)
                return render(request, 'whayp/index.html', {'posts': posts})
    context = {
        "form": form,
    }
    return render(request, 'whayp/register.html', context)


def photos(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'whayp/login.html')
    else:
        try:
            photo_ids = []
            for post in Post.objects.filter(user=request.user):
                for photo in post.photo_set.all():
                    photo_ids.append(photo.pk)
            users_photos = Photo.objects.filter(pk__in=photo_ids)
            if filter_by == 'favorites':
                users_photos = users_photos.filter(is_favorite=True)
        except Post.DoesNotExist:
            users_photos = []
        return render(request, 'whayp/photos.html', {
            'photo_list': users_photos,
            'filter_by': filter_by,
        })
