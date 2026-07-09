from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Task.objects.all()
        return Task.objects.filter(assigned_to=user)


class TaskCreateView(LoginRequiredMixin,CreateView):
    model = Task
    template_name = 'tasks/form.html'
    fields = ['title', 'description', 'assigned_to', 'customer', 'priority', 'status', 'due_date']
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        messages.success(self.request, "Task created successfully!")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tasks/form.html'
    fields = ['title', 'description', 'assigned_to', 'customer', 'priority', 'status', 'due_date']
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        messages.success(self.request, "Task updated successfully!")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/confirm_delete.html'
    success_url = reverse_lazy('tasks:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Task deleted!")
        return super().delete(request, *args, **kwargs)