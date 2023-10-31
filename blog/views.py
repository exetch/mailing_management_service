from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import BlogPost
from mailing.models import Mailing
from clients.models import Client
from django.urls import reverse_lazy
from django.utils.text import slugify
from .forms import BlogPostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin



class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_post_list.html'
    context_object_name = 'posts'
    ordering = ['-date_created']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='Менеджер').exists():
                context['total_mailings'] = Mailing.objects.all().count()
                context['active_mailings'] = Mailing.objects.filter(status__in=['started', 'created']).count()
                context['unique_clients'] = Client.objects.values('email').distinct().count()
            else:
                context['total_mailings'] = Mailing.objects.filter(user=self.request.user).count()
                context['active_mailings'] = Mailing.objects.filter(user=self.request.user,
                                                                    status__in=['started', 'created']).count()
                context['unique_clients'] = Client.objects.filter(user=self.request.user).values(
                    'email').distinct().count()
        else:
            pass

        context['random_posts'] = BlogPost.objects.order_by('?')[:3]

        return context


class BlogPostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'blog.add_blogpost'
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_post_form.html'
    success_url = reverse_lazy('blog_post_list')

    def form_valid(self, form):
        blog_post = form.save(commit=False)
        blog_post.slug = slugify(blog_post.title)
        blog_post.save()
        return super().form_valid(form)

class BlogPostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'blog.change_blogpost'
    model = BlogPost
    template_name = 'blog/blog_post_form.html'
    form_class = BlogPostForm
    context_object_name = 'blog_post'
class BlogPostDetailView(LoginRequiredMixin, DetailView):
    model = BlogPost
    template_name = 'blog/blog_post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        post.increment_views()
        return super().get(request, *args, **kwargs)

class BlogPostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'blog.delete_blogpost'
    model = BlogPost
    template_name = 'blog/blog_post_confirm_delete.html'
    context_object_name = 'blog_post'
    success_url = reverse_lazy('blog_post_list')

