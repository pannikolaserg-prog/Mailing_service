from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Client, Message, Mailing, Attempt
from .forms import ClientForm, MessageForm, MailingForm


class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx['total_mailings'] = Mailing.objects.count()
        ctx['active_mailings'] = Mailing.objects.filter(
            start_time__lte=now, end_time__gte=now, status='started'
        ).count()
        ctx['unique_clients'] = Client.objects.count()
        return ctx


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Клиент добавлен')
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение создано')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_mailings'):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка создана')
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Client.objects.filter(owner=self.request.user)
        return form


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self):
        obj = super().get_object()
        obj.update_status()
        return obj

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_mailings'):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempts = self.object.attempts.all()
        ctx['success_count'] = attempts.filter(status='success').count()
        ctx['failed_count'] = attempts.filter(status='failed').count()
        return ctx


class MailingSendView(LoginRequiredMixin, DetailView):
    model = Mailing

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def post(self, request, pk):
        mailing = self.get_object()
        mailing.update_status()

        if mailing.status != 'started':
            messages.error(request, 'Рассылка не может быть отправлена сейчас')
            return redirect('mailing:mailing_detail', pk=pk)

        ok, fail = 0, 0
        for client in mailing.recipients.all():
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    settings.DEFAULT_FROM_EMAIL,
                    [client.email],
                )
                Attempt.objects.create(
                    mailing=mailing, client=client, status='success', server_response='OK'
                )
                ok += 1
            except Exception as e:
                Attempt.objects.create(
                    mailing=mailing, client=client, status='failed', server_response=str(e)
                )
                fail += 1

        messages.success(request, f'Отправлено: {ok}, Ошибок: {fail}')
        return redirect('mailing:mailing_detail', pk=pk)
