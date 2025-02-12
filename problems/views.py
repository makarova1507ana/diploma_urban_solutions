from django.views.generic.base import TemplateView

from problems.models import *


class Index(TemplateView):

    template_name = 'index.html'
