from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def userLogin(res):
    return render(res, "login.html", {})


def home(res):
    my_list = ["Item 1", "Item 2", "Item 3", "Item 4"]
    return render(res, "index.html", {"items": my_list})


# Create your views here.
