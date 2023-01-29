from django.views.generic import  TemplateView,View
from django.http import HttpResponse
from django.shortcuts import render

class AboutView(TemplateView):
    template_name='about.html'

class TestView(View):
    def get(self,request):
        context={'list':list(range(3))}
        return render(request,'test.html',context)