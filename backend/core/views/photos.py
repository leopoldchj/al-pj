from core.services import PhotoService
from core.serializers import TargetAlbumSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class PhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, _, album_id):
        photos = PhotoService.get_photos_by_album_id(album_id)
        return Response(
            {"photos": photos, "album_id": album_id},
            status=status.HTTP_200_OK,
        )

    def post(self, request, album_id):
        photo_data = PhotoService.save_photo(album_id, request)
        return Response({"photo": photo_data}, status=status.HTTP_201_CREATED)


class PhotoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, album_id, photo_id):
        PhotoService.delete_photo(photo_id=photo_id, album_id=album_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, album_id, photo_id):
        photo_data = PhotoService.update_photo(
            photo_id=photo_id, album_id=album_id, data=request.data
        )
        return Response({"photo": photo_data}, status=status.HTTP_200_OK)


class PhotoMoveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, album_id, photo_id):
        serializer = TargetAlbumSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_album_id = serializer.validated_data["target_album_id"]

        photo_data = PhotoService.move_photo_to_album(
            photo_id=photo_id,
            target_album_id=target_album_id,
            user=request.user,
        )
        return Response({"photo": photo_data}, status=status.HTTP_200_OK)


class PhotoCopyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, album_id, photo_id):
        serializer = TargetAlbumSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_album_id = serializer.validated_data["target_album_id"]

        photo_data = PhotoService.copy_photo_to_album(
            photo_id=photo_id,
            target_album_id=target_album_id,
            user=request.user,
        )
        return Response({"photo": photo_data}, status=status.HTTP_201_CREATED)
