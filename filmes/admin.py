from .tasks import generate_video_sprites_task, calculate_video_duration
from django.utils.translation import gettext_lazy as _
from .models import Movies, Series, VideoSprite
from django.utils.html import format_html
from django.contrib import admin
from django.urls import reverse


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
class MovieAdmin(admin.ModelAdmin):
    inlines = [VideoSpriteInline]
    list_display = (
        "title_movie",
        "status_movie",
        "duration_in_minutes",
    )
    list_filter = ("status_movie", "gener_movie","title_movie")
    search_fields = ("id", "title_movie")
    readonly_fields = ("id",)

    actions = ["generate_sprites"]

    fieldsets = (
        (
            None,
            {
                "fields": ("id", "title_movie", "status_movie", "duration_all", "sprite_vtt"),
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
            generate_video_sprites_task.delay(video.id, "movie")

        self.message_user(
            request,
            _("%s vídeos enviados para geração de sprites.") % queryset.count(),
        )

    @admin.action(description=_("Generate Sprite Sheets"))
    def generate_sprites(self, request, queryset):
        for video in queryset:
            generate_video_sprites_task.delay(video.id, "episode")

        self.message_user(
            request,
            _("%s vídeos enviados para geração de sprites.") % queryset.count(),
        )

    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("sprites")
        )

    @admin.display(description=_("Content Name"))
    def get_target_name(self, obj):
        if obj.movie:
            return f"Filme: {obj.movie}"
        elif obj.episode:
            return f"Episódio: {obj.episode}"
        return "-"

    @admin.display(description=_("Type"))
    def get_target_type(self, obj):
        return obj.title_movie if obj else "-"

    @admin.display(description=_("Duration"), ordering="duration_all")
    def get_duration_fmt(self, obj):
        if not obj.duration_all:
            return "0s"

        total_seconds = int(obj.duration_all.total_seconds())

        m, s = divmod(total_seconds, 60)
        h, m = divmod(m, 60)
        
        minutes_with_seconds = f"{m:02d}:{s:02d}"
        
        if h == 0:
            return minutes_with_seconds
            
        return f"{h:02d}:{minutes_with_seconds}"

    @admin.display(description=_("Parent Link"))
    def link_to_parent(self, obj):
        target = getattr(obj, 'movie', None)

        if not target:
            return _("Orphaned Video")

        app_label = target._meta.app_label
        model_name = target._meta.model_name
        
        url = reverse(
                f"admin:{app_label}_{model_name}_change",
                args=[target.id],
        )
        return format_html(
                '<a href="{}" class="button" style="padding:3px 8px;">{}</a>',
                url,
                _("View Parent"),
        )

    @admin.display(description=_("Parent Object"))
    def link_to_parent_large(self, obj):
        target = getattr(obj, 'movie', None)

        if not target:
            return _("Orphaned Video")
        
        app_label = target._meta.app_label
        model = target._meta.model_name
        url = reverse(
            f"admin:{app_label}_{model}_change",
            args=[target.id],
        )
        return format_html(
            '<a href="{}">{} ({})</a>',
            url,
            obj,
            _("Click to edit"),
        )

    @admin.action(description=_("Generate Sprite Sheets"))
    def generate_sprites(self, request, queryset):
        for video in queryset:
            generate_video_sprites_task.delay(video.id)
        self.message_user(
            request,
            _("%s videos queued for sprite generation.") % queryset.count(),
        )


@admin.register(Series)
class SerieAdmin(admin.ModelAdmin):
    inlines = [VideoSpriteInline]
    list_display = (
        "title_serie",
        "status_series",
        "description",
    )
    list_filter = ("status_series", "gener_serie","title_serie")
    search_fields = ("id", "title_serie")
    readonly_fields = ("id",)

    actions = ["generate_sprites"]

    fieldsets = (
        (
            None,
            {
                "fields": ("id", "title_serie", "status_series"),
            },
        ),
        (
            "Files & Streaming",
            {
                "fields": ("file_episode", "hls_file"),
                "description": "Caminhos para o arquivo original e playlist HLS.",
            },
        ),
    )


    @admin.action(description=_("Generate Sprite Sheets"))
    def generate_sprites(self, request, queryset):
        for video in queryset:
            generate_video_sprites_task.delay(video.id, "episode")

        self.message_user(
            request,
            _("%s vídeos enviados para geração de sprites.") % queryset.count(),
        )


    def get_queryset(self, request):
        return (
            super().get_queryset(request).prefetch_related("sprites")
        )


    @admin.display(description=_("Content Name"))
    def get_target_name(self, obj):
        if obj.episode:
            return f"Ep: {obj.episode.title_episode} ({obj.episode.series.title_serie})"
        
        if obj.serie:
            return f"Série: {obj.serie.title_serie}"
        
        return "-"


    @admin.display(description=_("Type"))
    def get_target_type(self, obj):
        if obj.serie:
            return "Série"
        if obj.episode:
            return "Episódio"
        return "Desconhecido"


    @admin.display(description=_("Parent Link"))
    def link_to_parent(self, obj):
        target = getattr(obj, 'serie', None) or getattr(obj, 'episode', None)

        if not target:
            return _("Orphaned Video")

        app_label = target._meta.app_label
        model_name = target._meta.model_name
        
        url = reverse(
            f"admin:{app_label}_{model_name}_change",
            args=[target.id],
        )
        return format_html(
            '<a href="{}" class="button" style="padding:3px 8px;">{}</a>',
            url,
            _("View Parent"),
        )
     

    @admin.display(description=_("Parent Object"))
    def link_to_parent_large(self, obj):
        target = obj.serie or obj.episode

        if not target:
            return _("Orphaned Video")

        app_label = target._meta.app_label
        model_name = target._meta.model_name
        
        url = reverse(
            f"admin:{app_label}_{model_name}_change",
            args=[target.id],
        )
        
        return format_html(
            '<a href="{}">{} ({})</a>',
            url,
            str(target),
            _("Click to edit"),
        )


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
