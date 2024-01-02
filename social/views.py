from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.contrib.auth.decorators import login_required
from .forms import *
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import *
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator


def profile(request):
    # user=request.user
    posts = Post.objects.filter(author=request.user.id)
    try:
        user = User.objects.prefetch_related("followers", "following").get(id=request.user.id)
    except:
        return redirect("social:login")
    saved_posts = user.saved_posts.all()
    return render(request, "social/profile.html", {"saved_posts": saved_posts, "posts": posts,"user":user})


def log_out(request):
    logout(request)
    return HttpResponse("kharj shodi")
    # return redirect("blog:index")


# @login_required
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return render(request, "registration/register_done.html", {"user": user})
    else:
        form = UserRegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def edit_user(request):
    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=request.user, files=request.FILES)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = EditUserForm(instance=request.user)

    context = {
        "user_form": user_form,

    }
    return render(request, "registration/edit_user.html", context)


# def ticket(request):
#     sent=False
#     if request.method == "POST":
#         form = TicketForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             message=f'{cd["name"]}\n{cd["email"]}\n{cd["phone"]}'
#             # send_mail( cd['subject'] ,cd['message'],"sender@gmail.com" , ["reciever@gmail.com"] , fail_silently=False)
#             send_mail( cd['subject'] ,message ,"hoorieh.darvishi77@gmail.com" , ["hooridarvishi@gmail.com"] , fail_silently=False)
#             sent=True
#             # Ticket.objects.create( name=cd['name'], email=cd['email'],
#             #                       phone=cd['phone'])
#             return redirect("blog:index")
#     else:
#         form = TicketForm()
#     return render(request, "forms/ticket.html", {'form': form , "sent":sent})

def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = f'{cd["name"]}\n{cd["email"]}\n{cd["phone"]}'
            # send_mail( cd['subject'] ,cd['message'],"sender@gmail.com" , ["reciever@gmail.com"] , fail_silently=False)
            send_mail(cd['subject'], message, "hoorieh.darvishi77@gmail.com", ["hooridarvishi@gmail.com"],
                      fail_silently=False)
            messages.success(request, "ارسال شد")
            messages.warning(request, "its failed")
            # Ticket.objects.create( name=cd['name'], email=cd['email'],
            #                       phone=cd['phone'])

    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form, "messages": messages})


def post_list(request, tag_slug=None):
    query = None
    results = []
    if "query" in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            result1 = Post.objects.annotate(similarity=TrigramSimilarity("description", query)).filter(
                similarity__gt=0.1)
            result2 = Post.objects.annotate(similarity=TrigramSimilarity("title", query)).filter(similarity__gt=0.1)
            results = (result2 | result1).order_by("-similarity")
            print(result1, result2, results)
    posts = Post.objects.select_related("author").order_by("-total_liks")

    # posts = paginator.page(page_number)
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = Post.objects.filter(tags__in=[tag])
    page = request.GET.get("page")
    paginator = Paginator(posts, 2)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = []
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print("dddddd")
        return render(request, "social/list_ajax.html", {"posts": posts})
    #     اگر درخواست از ای جکس اومده:

    context = {
        'posts': posts,
        'tag': tag,
        "results": results,
        "query": query
    }
    return render(request, "social/list.html", context)


@login_required
def create_posts(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect("social:profile")
    else:
        form = CreatePostForm()
    return render(request, "forms/create_posts.html", {"form": form})


def post_detail(request, pstid):
    post = get_object_or_404(Post, id=pstid)
    # post_tags_ids=post.tags.all()
    post_tags_ids = post.tags.values_list("id", flat=True)
    # جایگزین ترای و اکسپتُُُُس
    print(post_tags_ids)
    similar_post = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count("tags")).order_by("-same_tags", "-created")[:5]
    # similar_post=Post.objects.annotate(ct=Count('tags'))
    # for p in similar_post:
    #     print(p.description , p.ct)
    comments = post.comment.all()
    form = CommentForm()
    # print("*******")
    context = {
        'post': post,
        'similar_post': similar_post,
        "comments": comments,
        "form": form
    }
    return render(request, "social/detail.html", context)


def comment_post(request, pk):
    comment = None
    post = get_object_or_404(Post, id=pk)
    print("pk=" + pk)
    print(post.author)
    print("*")
    if request.method == "POST":
        # print("***" * 100)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
    else:
        form = CommentForm()
    context = {
        "comment": comment,
        "form": form,
        "post": post
    }
    return render(request, "forms/comment.html", context)


@login_required
@require_POST
def like_post(request):
    print("xx")
    post_id = request.POST.get("post_id")
    print(post_id)
    if post_id is not None:
        print("none")
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if user in post.likes.all():
            print("pl:"+post.likes)
            post.likes.remove(user)
            liked = False
            print("remove*")
        else:
            print(post.likes)
            post.likes.add(user)
            liked = True
            print("add")
        post_likes_count = post.likes.count()
        response_data = {
            'liked': liked,
            'likes_count': post_likes_count,
        }
    else:
        response_data = {'error': 'invalid post_id'}
        print("else..")
    return JsonResponse(response_data)


@login_required
@require_POST
def save_post(request):
    post_id = request.POST.get("post_id")
    if post_id is not None:
        post = Post.objects.get(pk=post_id)
        user = request.user
        if user in post.saved_by.all():
            post.saved_by.remove(user)
            saved = False
        else:
            post.saved_by.add(user)
            saved = True
        return JsonResponse({"saved": saved})
    return JsonResponse({"error": "Invalid request"})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, "users/user_list.html", {"users": users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    followings=user.following.filter(username=username)
    return render(request, "users/user_detail.html", {"user": user,"followings":followings})

def contact(request, username, rel):
    user = User.objects.get(username=username)
    if rel == 'following':
        users = user.get_followings()
    else:
        users = user.get_followers()
    return render(request,'users/user_list.html', {'users': users})
# ای جکس به این ویو دیتا میفرستع   data:
@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get("id")
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            if request.user in user.followers.all():
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                follow = False
            else:
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                follow = True
            following_count = user.following.count()
            followers_count = user.followers.count()
            return JsonResponse(
                {'follow': follow, "followings_count": following_count, "followers_count": followers_count})
        # followings_count از سمت جی سون اومده
        except User.DoesNotExist:
            return JsonResponse({"error": "userdoes nott exist"})
    return JsonResponse({"error:invalid request"})


@login_required
def delete_posts(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect("social:profile")
    return render(request, "forms/delete_posts.html", {"post": post})


@login_required
def edit_posts(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':

        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect("social:profile")
    else:
        form = CreatePostForm(instance=post)
    return render(request, "forms/create_posts.html", {"form": form, "post": post})


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    return redirect("social:profile")
    # return render(request, "forms/delete_posts.html", {"image": image})
