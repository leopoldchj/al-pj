from core.models import Album, Photo
from core.serializers import PhotoSerializer
from core.dependencies import photo_repository
from core.websocket.utils import send_ws_message_to_user
from core.websocket.messages import WebSocketMessageType
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError
import logging

logger = logging.getLogger(__name__)


def _sanitize_for_log(value):
    """
    Return a log-safe string representation of `value` by removing
    newline characters that could be used for log injection.
    """
    text = str(value)
    # Replace CRLF, CR, and LF with a space to keep the log on a single line.
    return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")


class PhotoService:

    @staticmethod
    def _sanitize_for_log(value) -> str:
        text = str(value)
        return text.replace("\r", "").replace("\n", "")

    @staticmethod
    def get_photos_by_album_id(album_id):
        photos = Photo.objects.filter(album_id=album_id)
        photos = PhotoSerializer(photos, many=True).data
        return photos

    @classmethod
    def save_photo(cls, album_id, request):
        """Save a photo and broadcast the upload event."""
        data = request.data.copy()
        file = request.FILES

        try:
            album = Album.objects.get(pk=album_id)
        except Album.DoesNotExist:
            raise NotFound(f"Album with id {album_id} not found")

        if "image" in file and file["image"]:
            link = photo_repository.save_within_folder(
                file["image"], folder_album_id=album_id
            )
            data["image_url"] = link
        data["album"] = album_id

        serializer = PhotoSerializer(
            data=data, context={"request": request, "album": album}
        )
        serializer.is_valid(raise_exception=True)
        photo = serializer.save(album=album)
        photo_data = PhotoSerializer(photo).data

        safe_album_id = cls._sanitize_for_log(album_id)
        safe_photo_id = cls._sanitize_for_log(photo.id)
        logger.info(f"Photo uploaded to album {safe_album_id}: {safe_photo_id}")

        # Broadcast the upload event
        cls._broadcast_change(
            WebSocketMessageType.PHOTO_UPLOADED,
            {"data": photo_data, "album_id": album_id},
        )

        return photo_data

    @classmethod
    def delete_photo(cls, photo_id: int, album_id: int) -> None:
        """Delete a photo and broadcast the deletion event."""
        try:
            photo = Photo.objects.get(pk=photo_id, album_id=album_id)
        except Photo.DoesNotExist:
            raise NotFound(f"Photo with id {photo_id} not found in album {album_id}")

        deleted_id = photo.id
        photo.delete()

        safe_album_id = cls._sanitize_for_log(album_id)
        safe_deleted_id = cls._sanitize_for_log(deleted_id)
        logger.info(f"Photo deleted from album {safe_album_id}: {safe_deleted_id}")

        # Broadcast the deletion event
        cls._broadcast_change(
            WebSocketMessageType.PHOTO_DELETED, {"id": deleted_id, "album_id": album_id}
        )

    @classmethod
    def update_photo(cls, photo_id: int, album_id: int, data: dict) -> dict:
        """Update a photo and broadcast the update event."""
        try:
            photo = Photo.objects.get(pk=photo_id, album_id=album_id)
        except Photo.DoesNotExist:
            raise NotFound(f"Photo with id {photo_id} not found in album {album_id}")

        serializer = PhotoSerializer(photo, data=data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        photo = serializer.save()
        photo_data = PhotoSerializer(photo).data

        safe_album_id = cls._sanitize_for_log(album_id)
        safe_photo_id = cls._sanitize_for_log(photo.id)
        logger.info(f"Photo updated in album {safe_album_id}: {safe_photo_id}")

        # Broadcast the update event
        cls._broadcast_change(
            WebSocketMessageType.PHOTO_UPDATED,
            {"data": photo_data, "album_id": album_id},
        )

        return photo_data

    @classmethod
    def move_photo_to_album(cls, photo_id: int, target_album_id: int, user) -> dict:
        """Move a photo to another album by updating its FK."""
        try:
            photo = Photo.objects.get(pk=photo_id)
        except Photo.DoesNotExist:
            raise NotFound(f"Photo with id {photo_id} not found")

        try:
            target_album = Album.objects.get(pk=target_album_id)
        except Album.DoesNotExist:
            raise NotFound(f"Album with id {target_album_id} not found")

        source_album_id = photo.album_id
        if source_album_id == target_album_id:
            raise ValidationError("La photo est déjà dans cet album.")

        photo.album = target_album
        photo.save()

        photo_data = PhotoSerializer(photo).data

        safe_photo_id = cls._sanitize_for_log(photo_id)
        safe_target = cls._sanitize_for_log(target_album_id)
        logger.info(f"Photo {safe_photo_id} moved to album {safe_target}")

        cls._broadcast_change(
            WebSocketMessageType.PHOTO_MOVED,
            {
                "data": photo_data,
                "source_album_id": source_album_id,
                "target_album_id": target_album_id,
            },
        )

        return photo_data

    @classmethod
    def copy_photo_to_album(cls, photo_id: int, target_album_id: int, user) -> dict:
        """Copy a photo to another album with S3 server-side copy."""
        try:
            photo = Photo.objects.get(pk=photo_id)
        except Photo.DoesNotExist:
            raise NotFound(f"Photo with id {photo_id} not found")

        try:
            target_album = Album.objects.get(pk=target_album_id)
        except Album.DoesNotExist:
            raise NotFound(f"Album with id {target_album_id} not found")

        if photo.album_id == target_album_id:
            raise ValidationError("La photo est déjà dans cet album.")

        # S3 server-side copy to a new key
        new_url = photo_repository.copy_file(photo.image_url, target_album_id)

        # Create a new Photo entry pointing to the copied file
        new_photo = Photo.objects.create(
            album=target_album,
            image_url=new_url,
            caption=photo.caption,
            location=photo.location,
        )

        photo_data = PhotoSerializer(new_photo).data

        safe_photo_id = cls._sanitize_for_log(photo_id)
        safe_target = cls._sanitize_for_log(target_album_id)
        logger.info(f"Photo {safe_photo_id} copied to album {safe_target}")

        cls._broadcast_change(
            WebSocketMessageType.PHOTO_COPIED,
            {"data": photo_data, "album_id": target_album_id},
        )

        return photo_data

    @staticmethod
    def _broadcast_change(message_type: WebSocketMessageType, message_data: dict):
        """Broadcast a photo change to all authenticated users."""
        recipients = User.objects.all().values_list("id", flat=True)

        for uid in recipients:
            send_ws_message_to_user(uid, message_type, message_data)
