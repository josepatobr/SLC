from django.shortcuts import render


def checkout(request):
    return render(request, 'checkout.html')


def payment_success(request):
    return render(request, 'success.html')


def payment_cancel(request):
    return render(request, 'cancel.html')

