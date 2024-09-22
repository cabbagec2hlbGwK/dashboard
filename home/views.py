from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings


def userLogin(res):
    return render(res, "login.html", {})


def home(res):
    DB_CONNECTION = settings.getConnection()
    totalMessages = DB_CONNECTION.getAllRequestsSum()
    totalApproved = DB_CONNECTION.getApprovedRequestsSum()
    totalDeny = DB_CONNECTION.getDeniedRequestsSum()
    totalExpired = DB_CONNECTION.getExpireddMessagesSum()
    totalActive = DB_CONNECTION.getActiveMessagesSum()
    data = DB_CONNECTION.getData()
    values = {
        "message": totalMessages,
        "approved": totalApproved,
        "deny": totalDeny,
        "expired": totalExpired,
        "active": totalActive,
        "data": data,
    }
    DB_CONNECTION.close()
    del DB_CONNECTION
    print(
        f"Message :{totalMessages}, Approved :{totalApproved}, Deny :{totalDeny}, Expired :{totalExpired}, Active :{totalActive}, data :{data}"
    )
    return render(res, "dash.html", {"items": values})


# Create your views here.
