from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import Customer, Lead
from notifications.email_utils import send_lead_converted_email



class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/list.html'
    context_object_name = 'customers'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Customer.objects.all()
        return Customer.objects.filter(assigned_worker=user)


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = 'customers/form.html'
    fields = ['name', 'phone', 'email', 'address', 'company', 'status', 'assigned_worker', 'notes']
    success_url = reverse_lazy('customers:list')

    def form_valid(self, form):
        messages.success(self.request, "Customer added successfully!")
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'customers/form.html'
    fields = ['name', 'phone', 'email', 'address', 'company', 'status', 'assigned_worker', 'notes']
    success_url = reverse_lazy('customers:list')

    def form_valid(self, form):
        messages.success(self.request, "Customer updated successfully!")
        return super().form_valid(form)


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/confirm_delete.html'
    success_url = reverse_lazy('customers:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Customer deleted!")
        return super().delete(request, *args, **kwargs)


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'customers/lead_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Lead.objects.all()
        return Lead.objects.filter(assigned_to=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_leads'] = Lead.objects.filter(status='new').count()
        context['contacted'] = Lead.objects.filter(status='contacted').count()
        context['interested'] = Lead.objects.filter(status='interested').count()
        context['converted'] = Lead.objects.filter(status='converted').count()
        return context


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    template_name = 'customers/lead_form.html'
    fields = ['name', 'phone', 'email', 'address', 'company',
              'source', 'status', 'assigned_to', 'notes', 'follow_up_date']
    success_url = reverse_lazy('customers:lead_list')

    def form_valid(self, form):
        messages.success(self.request, "Lead added successfully!")
        return super().form_valid(form)


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    template_name = 'customers/lead_form.html'
    fields = ['name', 'phone', 'email', 'address', 'company',
              'source', 'status', 'assigned_to', 'notes', 'follow_up_date']
    success_url = reverse_lazy('customers:lead_list')

    def form_valid(self, form):
        messages.success(self.request, "Lead updated!")
        return super().form_valid(form)


class LeadConvertView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)

        customer = Customer.objects.create(
            name=lead.name,
            phone=lead.phone,
            email=lead.email,
            address=lead.address,
            company=lead.company,
            assigned_worker=lead.assigned_to,
            status='active',
            notes=f"Converted from lead. Source: {lead.source}"
        )

        lead.status = 'converted'
        lead.converted_at = timezone.now()
        lead.save()

        send_lead_converted_email(lead, customer)

        messages.success(request, f"{lead.name} converted to customer!")
        return redirect('customers:lead_list')