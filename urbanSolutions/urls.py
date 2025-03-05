
from django.contrib import admin
from django.urls import path, include

from .views import Index, ErrorView, About, generate_report_pdf
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

handler400 = lambda request, exception: ErrorView.as_view()(request, status_code=400)
handler403 = lambda request, exception: ErrorView.as_view()(request, status_code=403)
handler404 = lambda request, exception: ErrorView.as_view()(request, status_code=404)
handler500 = lambda request: ErrorView.as_view()(request, status_code=500)

urlpatterns = [
    path('admin/reports/<int:report_id>/generate_pdf/', generate_report_pdf, name='generate_report_pdf'),

    path('admin/', admin.site.urls),
    path('', Index.as_view(), name='index'),
    path('reports/', include('reports.urls', namespace='reports')),
    path('users/', include('users.urls', namespace='users')),
    path('about/', About.as_view(), name='about'),

]
admin.site.site_header = "Администрирование сайта Городские решения"

#admin.site.index_title = "TITLE"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

