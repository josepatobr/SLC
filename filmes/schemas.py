from .models import VideoSprite, VideoTrack
from ninja import ModelSchema


class VideoSpriteSchema(ModelSchema):
    class Meta:
        model = VideoSprite
        exclude = ["id", "video", "created_at"]


class VideoTrackSchema(ModelSchema):
    class Meta:
        model = VideoTrack
        exclude = [
            "id",
            "video",
            "audio_playlist",
            "source_audio_index",
            "source_subtitle_index",
            "created_at",
            "updated_at",
        ]
