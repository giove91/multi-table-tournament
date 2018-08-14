from django.shortcuts import render
from django.views.generic.base import TemplateView

from .models import *



class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        tournament = Tournament.objects.latest()
        
        context = super().get_context_data(**kwargs)
        context['tournament'] = tournament
        return context

