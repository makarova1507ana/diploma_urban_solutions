from django.urls import path, re_path
import problems.views as problems

urlpatterns = [

    path('', problems.Index.as_view(), name='index'),
    # path('search/', problems.ProblemsList.as_view(), name='search'),
    #
    # path('problem/suggest/', problems.SuggestProblem.as_view()),
    # path('problem/<int:pk>/', problems.ProblemDetailView.as_view()),
    #
    # path('cats/', problems.categories, name="media"),
    #
    # re_path(r"^archive/(?P<year>(1|2)\d{3})/$", problems.archive),

]