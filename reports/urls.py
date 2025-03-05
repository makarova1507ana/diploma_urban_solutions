from django.urls import path, re_path
import reports.views as reports

# Установка пространства имен для приложения "reports"
app_name = "reports"

urlpatterns = [
    path('', reports.Reports.as_view(), name='reports'),

    path('topics/', reports.TopicsPage.as_view(), name='topics'),  # Создаем путь для страницы тем
    path('topics/<int:pk>/', reports.TopicDetailView.as_view(), name='topic_detail'),
    path('report/step1/', reports.Step1View.as_view(), name='step1'),
    path('report/step2/', reports.Step2View.as_view(), name='step2'),
    path('report/step3/', reports.Step3View.as_view(), name='step3'),
    path('report/<int:pk>/', reports.ReportDetailView.as_view(), name='report_detail'),

    path('report/<int:report_id>/add_comment/', reports.AddCommentView.as_view(), name='add_comment'),

    path('report/map/', reports.Map.as_view(), name='map'),
    path('upload/', reports.images_upload, name='upload')

    # re_path(r"^archive/(?P<year>(1|2)\d{3})/$", reports.archive),

]