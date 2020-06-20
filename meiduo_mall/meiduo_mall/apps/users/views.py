from django.shortcuts import render

# Create your views here.
from .models import User
from django.views import View
from django import http

class UsernameCountView(View):

    def get(self, request, username):

        count = User.objects.filter(username=username).count()

        return http.JsonResponse({
            'code':200,
            'errmsg':'ok',
            'count':count
        })


class MobileCountView(View):

    def get(self, request, mobile):

        count = User.objects.filter(mobile=mobile).count()

        return http.JsonResponse({
            'code':200,
            'errmsg':'ok',
            'count':count
        })
