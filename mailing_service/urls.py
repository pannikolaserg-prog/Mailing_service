from django.contrib import admin
from django.urls import path, include  # добавить include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailing.urls')),
    path('accounts/', include('allauth.urls')),  # все URL для входа/регистрации/восстановления
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # опционально
]