from django.urls import path, re_path
import reports.views as reports

# Установка пространства имен для приложения "reports"
app_name = "reports"

urlpatterns = [

    path('topics/', reports.TopicsPage.as_view(), name='topics'),  # Создаем путь для страницы тем
    path('topics/<int:pk>/', reports.TopicDetailView.as_view(), name='topic_detail'),
    path('report/step1/', reports.Step1View.as_view(), name='step1'),
    path('report/step2/', reports.Step2View.as_view(), name='step2'),
    path('report/step3/', reports.Step3View.as_view(), name='step3'),

    # path('search/', reports.ProblemsList.as_view(), name='search'),
    #
    # path('problem/suggest/', reports.SuggestProblem.as_view()),
    # path('problem/<int:pk>/', reports.ProblemDetailView.as_view()),
    #
    # path('cats/', reports.categories, name="media"),
    #
    # re_path(r"^archive/(?P<year>(1|2)\d{3})/$", reports.archive),

]