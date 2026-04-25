from django.contrib import admin
from .models import Client, Message, Mailing, Attempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'comment']
    search_fields = ['email', 'full_name']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'body_preview']

    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body

    body_preview.short_description = 'Тело письма'


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'status', 'start_time', 'end_time']
    list_filter = ['status']
    filter_horizontal = ['recipients']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['mailing', 'status', 'attempt_time', 'server_response_preview']
    list_filter = ['status']

    def server_response_preview(self, obj):
        return obj.server_response[:50] + '...' if len(obj.server_response) > 50 else obj.server_response

    server_response_preview.short_description = 'Ответ сервера'
