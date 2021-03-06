from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()

from insane_app.models import Story, Product, Category, StoryLike, StoryComment,\
    StoryCommentLike


class SanityRequiredMixin(object):
    sanity_required = 0

    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.sanity < self.sanity_required:
            request.user.profile.sanity += 5
            request.user.profile.save()
            raise Http404("not enough sanity")
        else:
            return super(SanityRequiredMixin, self).dispatch(
                request, *args, kwargs)


class StoryListView(ListView):

    model = Story
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class StoryDetailView(DetailView):

    model = Story

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        comments = context['story'].storycomment_set.all()

        if self.request.user.is_authenticated:
            try:
                story_like = StoryLike.objects.get(story__pk = kwargs['object'].pk,
                    user = self.request.user)
                context['story'].liked = True

            except StoryLike.DoesNotExist:
                pass

            for comment in comments:
                try:
                    comment_like = StoryCommentLike.objects.get(
                        comment = comment, user = self.request.user
                    )
                    comment.liked = True
                except StoryCommentLike.DoesNotExist:
                    pass


        context['comments'] = comments
        return context


def like_story(request, pk):
    if not request.user.is_authenticated:
        return HttpResponse(-1)

    object, created = StoryLike.objects.get_or_create(
        user=request.user,
        story=Story.objects.get(pk=pk)
    )

    if not created:
        object.delete()
    else:
        created = 1

    return HttpResponse(created)


def like_story_comment(request, story_pk, comment_pk):
    if not request.user.is_authenticated:
        return HttpResponse(-1)

    object, created = StoryCommentLike.objects.get_or_create(
        user=request.user,
        comment=StoryComment.objects.get(pk=comment_pk)
    )

    if not created:
        object.delete()
    else:
        created = 1

    return HttpResponse(created)


class StoryCreateView(SanityRequiredMixin, LoginRequiredMixin, CreateView):
    model = Story
    fields = ('name', 'body')

    sanity_required = 4

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        profile = self.request.user.profile
        profile.sanity -= self.sanity_required
        profile.save()

        return redirect(self.get_success_url())


class ProductListView(ListView):

    model = Product
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["category_set"] = Category.objects.all().order_by('name')
        return context

    def get_queryset(self):
        categories_id = self.request.GET.getlist('categories')
        if categories_id:
            return self.model.objects.filter(categories__pk__in = categories_id)
        else:
            return self.model.objects.all()


class ProductDetailView(DetailView):

    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class ProductCreateView(SanityRequiredMixin, LoginRequiredMixin, CreateView):

    model = Product
    fields = ('name', 'description', 'price')

    success_url = '/insane/market/'

    sanity_required = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_set'] = Category.objects.all()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        categories = self.request.POST.getlist('categories', ())
        self.object.save()
        profile = self.request.user.profile
        profile.sanity -= self.sanity_required
        profile.save()

        if categories:
            self.object.categories.set(Category.objects.filter(pk__in=categories))
        return redirect(self.get_success_url())


class SignUpView(CreateView):
    model = User
    fields = ('username', 'password', )

    template_name = 'insane_accounts/signup.html'
