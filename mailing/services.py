from django.core.cache import cache
from .models import Client, Message, Mailing


def get_cached_stats():
    stats = cache.get('mailing_stats')
    if stats is None:
        stats = {
            'total_clients': Client.objects.count(),
            'total_messages': Message.objects.count(),
            'total_mailings': Mailing.objects.count(),
        }
        cache.set('mailing_stats', stats, 300)
    return stats


def clear_stats_cache():
    cache.delete('mailing_stats')
