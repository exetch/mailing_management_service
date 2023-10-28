from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import BlogPost
from django.urls import reverse_lazy
from django.utils.text import slugify
from .forms import BlogPostForm



class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_post_list.html'
    context_object_name = 'posts'
    ordering = ['-date_created']

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by('-date_created')[:3]

class BlogPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blog_post_form.html'
    success_url = reverse_lazy('blog_post_list')

    def form_valid(self, form):
        blog_post = form.save(commit=False)
        blog_post.slug = slugify(blog_post.title)
        blog_post.save()
        return super().form_valid(form)

class BlogPostUpdateView(UpdateView):
    model = BlogPost
    template_name = 'blog/blog_post_form.html'
    form_class = BlogPostForm
    context_object_name = 'blog_post'
class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        post.increment_views()
        return super().get(request, *args, **kwargs)





class BlogPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'blog/blog_post_confirm_delete.html'
    context_object_name = 'blog_post'
    success_url = reverse_lazy('blog_post_list')

