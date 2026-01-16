from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig


class UploadConfig(AppConfig):
    verbose_name = _("Upload")
    name = "upload"
