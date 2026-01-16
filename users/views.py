from django.shortcuts import render, get_object_or_404, redirect
from .models import CustomUserChangeForm, CustomUser


def profile(request, id):
    user = CustomUser.objects.get(id=id)
    return render(request, "profile.html", {"user": user})


def profile_edit(request, id):
    user_to_edit = get_object_or_404(CustomUser, id=id)

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            form.save()
            return redirect("profile", id=user_to_edit.id)
    else:
        form = CustomUserChangeForm(instance=user_to_edit)
    return render(request, "profile_edit.html", {"form": form, "user": user_to_edit})
