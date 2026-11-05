from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('school/', include('school.urls', namespace='school')),
    path('students/', include('students.urls', namespace='students')),
    path('academics/', include('academics.urls', namespace='academics')),
    path('attendance/', include('attendance_payments.urls', namespace='attendance_payments')),
    path('api/', include('api.urls', namespace='api')),
    path('', include('school.urls_dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
