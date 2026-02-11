from .tasks import generate_video_sprites_task, calculate_video_duration
from .models import Episode, Movies, Series, VideoSprite
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin
from django.urls import reverse


admin.site.register(Series)
admin.site.register(Episode)


class VideoSpriteInline(admin.TabularInline):
    model = VideoSprite
    extra = 0
    ordering = ("start_time",)
    fields = (
        "start_time",
        "end_time",
        "interval",
        "grid_info",
        "image",
    )
    readonly_fields = ("sprite_preview", "grid_info")
    can_delete = True
    show_change_link = True
    verbose_name = _("Sprite Sheet")
    verbose_name_plural = _("Sprite Sheets")

    @admin.display(description=_("Preview"))
    def sprite_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 40px; border: 1px solid #ccc;" />',
                obj.image.url,
            )
        return "-"

    @admin.display(description=_("Grid (WxH)"))
    def grid_info(self, obj):
        return f"{obj.columns}x{obj.rows} ({obj.frame_width}px)"


@admin.register(Movies)
class VideoAdmin(admin.ModelAdmin):
    inlines = [VideoSpriteInline]
    list_display = (
        "title",
        "status_movie",
        "duration_in_minutes",
    )
    list_filter = ("status_movie", "gener_movie")
    search_fields = ("id", "title")
    readonly_fields = ("id",)

    actions = ["generate_sprites"]

    fieldsets = (
        (
            None,
            {
                "fields": ("id", "status_movie", "duration_all", "sprite_vtt"),
            },
        ),
        (
            "Files & Streaming",
            {
                "fields": ("file_movie", "hls_file"),
                "description": "Caminhos para o arquivo original e playlist HLS.",
            },
        ),
    )

    @admin.action(description="Gerar Sprite Sheets")
    def generate_sprites(self, request, queryset):
        for video in queryset:
            calculate_video_duration.delay(video.id, "movie")
        self.message_user(
            request, f"{queryset.count()} vídeos enviados para processamento."
        )

    @admin.action(description=_("Generate Sprite Sheets"))
    def generate_sprites(self, request, queryset):
        for video in queryset:
            model_type = "movie" if video.content_type.model == "movies" else "episode"
            generate_video_sprites_task.delay(video.id, model_type)

        self.message_user(
            request,
            _("%s vídeos enviados para geração de sprites.") % queryset.count(),
        )

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("content_object", "sprites")
        )

    @admin.display(description=_("Content Name"))
    def get_target_name(self, obj):
        return str(obj.content_object) if obj.content_object else "-"

    @admin.display(description=_("Type"))
    def get_target_type(self, obj):
        return obj.content_type.model.title() if obj.content_type else "-"

    @admin.display(description=_("Duration"), ordering="duration")
    def get_duration_fmt(self, obj):
        if not obj.duration:
            return "0s"
        m, s = divmod(obj.duration, 60)
        h, m = divmod(m, 60)
        minutes_with_seconds = f"{m:02d}:{s:02d}"
        if h == 0:
            return minutes_with_seconds
        two_decimal = 10
        hour = f"{h:02d}" if h > two_decimal else f"{h:01d}"
        return f"{hour}:{minutes_with_seconds}"

    @admin.display(description=_("Parent Link"))
    def link_to_parent(self, obj):
        if obj.content_object:
            ct = obj.content_type
            url = reverse(
                f"admin:{ct.app_label}_{ct.model}_change",
                args=[obj.object_id],
            )
            return format_html(
                '<a href="{}" class="button" style="padding:3px 8px;">{}</a>',
                url,
                _("View Parent"),
            )
        return "-"

    @admin.display(description=_("Parent Object"))
    def link_to_parent_large(self, obj):
        if obj.content_object:
            ct = obj.content_type
            url = reverse(
                f"admin:{ct.app_label}_{ct.model}_change",
                args=[obj.object_id],
            )
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.content_object,
                _("Click to edit"),
            )
        return _("Orphaned Video")

    @admin.action(description=_("Generate Sprite Sheets"))
    def generate_sprites(self, request, queryset):
        for video in queryset:
            generate_video_sprites_task.delay(video.id)
        self.message_user(
            request,
            _("%s videos queued for sprite generation.") % queryset.count(),
        )


@admin.register(VideoSprite)
class VideoSpriteAdmin(admin.ModelAdmin):
    list_display = (
        "sprite_preview_large",
        "time_range",
        "interval",
        "dimensions",
    )

    list_filter = ("interval",)
    search_fields = ("video__title", "video__id")
    readonly_fields = ("sprite_preview_detail",)

    fieldsets = (
        (
            "File Info",
            {
                "fields": ("video", "image", "sprite_preview_detail"),
            },
        ),
        (
            "Timing",
            {
                "fields": (("start_time", "end_time"), "interval"),
            },
        ),
        (
            "Technical Dimensions",
            {
                "fields": (("frame_width", "frame_height"), ("columns", "rows")),
            },
        ),
    )

    @admin.display(description="Preview")
    def sprite_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px;"/>', obj.image.url
            )
        return "-"

    @admin.display(description="Full Preview")
    def sprite_preview_detail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px;"/>', obj.image.url
            )
        return "-"

    @admin.display(description="Time Range")
    def time_range(self, obj):
        return f"{obj.start_time}s - {obj.end_time}s"

    @admin.display(description="Thumb Size")
    def dimensions(self, obj):
        return f"{obj.frame_width}x{obj.frame_height}px"
