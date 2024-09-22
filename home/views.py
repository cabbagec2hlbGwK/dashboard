from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings


def userLogin(res):
    return render(res, "login.html", {})


def home(res):
    totalMessages = settings.DB_CONNECTION.getAllRequestsSum()
    totalApproved = settings.DB_CONNECTION.getApprovedRequestsSum()
    totalDeny = settings.DB_CONNECTION.getDeniedRequestsSum()
    totalExpired = settings.DB_CONNECTION.getExpireddMessagesSum()
    totalActive = settings.DB_CONNECTION.getActiveMessagesSum()
    data = settings.DB_CONNECTION.getData()
    values = {
        "message": totalMessages,
        "approved": totalApproved,
        "deny": totalDeny,
        "expired": totalExpired,
        "active": totalActive,
        "data": data,
    }
    print(
        f"Message :{totalMessages}, Approved :{totalApproved}, Deny :{totalDeny}, Expired :{totalExpired}, Active :{totalActive}, data :{data}"
    )
    return render(res, "index.html", {"items": values})


# Create your views here.
