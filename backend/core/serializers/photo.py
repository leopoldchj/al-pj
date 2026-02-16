from rest_framework import serializers
from ..models.photo import Photo
from .album import AlbumSerializer


class PhotoSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Photo
        fields = [
            "id",
            "album",
            "image_url",
            "caption",
            "created_at",
            "updated_at",
            "location",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Block image_url modification on update (PATCH) — pure DB edit only
        if self.instance is not None:
            self.fields["image_url"].read_only = True

    def create(self, validated_data):
        request = self.context.get("request")
        if request and not request.user.is_authenticated:
            return None
        album = self.context.get("album")
        if not album:
            raise serializers.ValidationError({"album": "Album manquant"})

        return Photo.objects.create(album=album, **validated_data)


class TargetAlbumSerializer(serializers.Serializer):
    target_album_id = serializers.IntegerField()
