import unittest
from unittest.mock import MagicMock, patch

from core.services.photo_service import PhotoService

TEST_ALBUM_ID = 1
TEST_PHOTO_ID = 1
TEST_PHOTO_URL = "https://bucket.s3.amazonaws.com/1/photo.jpg"
TEST_PHOTO_CAPTION = "Beautiful sunset"
TEST_PHOTO_LOCATION = "Paris, France"
TEST_FILE_NAME = "sunset.jpg"


class TestPhotoServiceGetPhotosByAlbumId(unittest.TestCase):
    """Tests for PhotoService.get_photos_by_album_id method."""

    def setUp(self):
        """Set up test fixtures."""
        self.serialized_photos = [
            {
                "id": 1,
                "image_url": TEST_PHOTO_URL,
                "caption": TEST_PHOTO_CAPTION,
                "location": TEST_PHOTO_LOCATION,
            },
            {
                "id": 2,
                "image_url": "https://bucket.s3.amazonaws.com/1/photo2.jpg",
                "caption": "Another photo",
                "location": None,
            },
        ]

    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    def test_get_photos_by_album_id_filters_by_album_id(
        self, mock_photo_model, mock_serializer_class
    ):

        mock_queryset = MagicMock()
        mock_photo_model.objects.filter.return_value = mock_queryset
        mock_serializer_class.return_value.data = self.serialized_photos

        PhotoService.get_photos_by_album_id(TEST_ALBUM_ID)

        mock_photo_model.objects.filter.assert_called_once_with(album_id=TEST_ALBUM_ID)

    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    def test_get_photos_by_album_id_returns_serialized_photos(
        self, mock_photo_model, mock_serializer_class
    ):

        mock_queryset = MagicMock()
        mock_photo_model.objects.filter.return_value = mock_queryset
        mock_serializer_class.return_value.data = self.serialized_photos

        result = PhotoService.get_photos_by_album_id(TEST_ALBUM_ID)

        self.assertEqual(result, self.serialized_photos)

    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    def test_get_photos_by_album_id_uses_many_serializer(
        self, mock_photo_model, mock_serializer_class
    ):

        mock_queryset = MagicMock()
        mock_photo_model.objects.filter.return_value = mock_queryset
        mock_serializer_class.return_value.data = self.serialized_photos

        PhotoService.get_photos_by_album_id(TEST_ALBUM_ID)

        mock_serializer_class.assert_called_once_with(mock_queryset, many=True)

    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    def test_get_photos_by_album_id_when_empty_returns_empty_list(
        self, mock_photo_model, mock_serializer_class
    ):

        mock_queryset = MagicMock()
        mock_photo_model.objects.filter.return_value = mock_queryset
        mock_serializer_class.return_value.data = []

        result = PhotoService.get_photos_by_album_id(TEST_ALBUM_ID)

        self.assertEqual(result, [])


class TestPhotoServiceSavePhoto(unittest.TestCase):
    """Tests for PhotoService.save_photo method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_file = MagicMock()
        self.mock_file.name = TEST_FILE_NAME

        self.mock_request = MagicMock()
        self.mock_request.data = MagicMock()
        self.mock_request.data.copy.return_value = {
            "caption": TEST_PHOTO_CAPTION,
            "location": TEST_PHOTO_LOCATION,
        }
        self.mock_request.FILES = {"image": self.mock_file}

        self.mock_album = MagicMock()
        self.mock_album.id = TEST_ALBUM_ID

        self.serialized_photo = {
            "id": TEST_PHOTO_ID,
            "image_url": TEST_PHOTO_URL,
            "caption": TEST_PHOTO_CAPTION,
            "location": TEST_PHOTO_LOCATION,
        }

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_uploads_image_to_album_folder(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

        mock_photo_repo.save_within_folder.assert_called_once_with(
            self.mock_file, folder_album_id=TEST_ALBUM_ID
        )

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_fetches_album_by_id(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

        mock_album_model.objects.get.assert_called_once_with(pk=TEST_ALBUM_ID)

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_returns_serialized_photo(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        result = PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

        self.assertEqual(result, self.serialized_photo)

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_passes_album_context_to_serializer(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

        # First call is for validation (with context), second is for serialization
        first_call_args = mock_serializer_class.call_args_list[0]
        context = first_call_args[1]["context"]
        self.assertEqual(context["album"], self.mock_album)
        self.assertEqual(context["request"], self.mock_request)

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_saves_with_album_reference(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

        mock_serializer.save.assert_called_once_with(album=self.mock_album)

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_without_image_does_not_upload(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_request = MagicMock()
        mock_request.data = MagicMock()
        mock_request.data.copy.return_value = {
            "caption": TEST_PHOTO_CAPTION,
        }
        mock_request.FILES = {}
        mock_album_model.objects.get.return_value = self.mock_album
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        PhotoService.save_photo(TEST_ALBUM_ID, mock_request)

        mock_photo_repo.save_within_folder.assert_not_called()

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_sets_image_url_from_upload(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user,
        mock_ws_send,
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user.objects.all.return_value.values_list.return_value = [1]

        PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

        # First call is for validation (with data)
        first_call_args = mock_serializer_class.call_args_list[0]
        data_passed = first_call_args[1]["data"]
        self.assertEqual(data_passed["image_url"], TEST_PHOTO_URL)

    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_with_invalid_data_raises_exception(
        self, mock_photo_repo, mock_album_model, mock_serializer_class
    ):

        mock_album_model.objects.get.return_value = self.mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL
        mock_serializer = MagicMock()
        mock_serializer.is_valid.side_effect = Exception("Validation error")
        mock_serializer_class.return_value = mock_serializer

        with self.assertRaises(Exception):
            PhotoService.save_photo(TEST_ALBUM_ID, self.mock_request)

    @patch("core.services.photo_service.Album")
    def test_save_photo_with_nonexistent_album_raises_exception(self, mock_album_model):
        mock_album_model.DoesNotExist = Exception
        mock_album_model.objects.get.side_effect = mock_album_model.DoesNotExist

        with self.assertRaises(Exception):
            PhotoService.save_photo(999, self.mock_request)


class TestPhotoServiceDeletePhoto(unittest.TestCase):
    """Tests for PhotoService.delete_photo method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_photo = MagicMock()
        self.mock_photo.id = TEST_PHOTO_ID

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.Photo")
    def test_delete_photo_deletes_from_database(
        self, mock_photo_model, mock_user_model, mock_ws_send
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1, 2]

        PhotoService.delete_photo(TEST_PHOTO_ID, TEST_ALBUM_ID)

        self.mock_photo.delete.assert_called_once()

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.Photo")
    def test_delete_photo_broadcasts_deletion_event(
        self, mock_photo_model, mock_user_model, mock_ws_send
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1, 2]

        PhotoService.delete_photo(TEST_PHOTO_ID, TEST_ALBUM_ID)

        # Should broadcast to all users
        assert mock_ws_send.call_count == 2

    @patch("core.services.photo_service.Photo")
    def test_delete_photo_raises_not_found_for_nonexistent_photo(
        self, mock_photo_model
    ):
        from rest_framework.exceptions import NotFound

        mock_photo_model.DoesNotExist = Exception
        mock_photo_model.objects.get.side_effect = mock_photo_model.DoesNotExist

        with self.assertRaises(NotFound):
            PhotoService.delete_photo(999, TEST_ALBUM_ID)


class TestPhotoServiceUpdatePhoto(unittest.TestCase):
    """Tests for PhotoService.update_photo method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_photo = MagicMock()
        self.mock_photo.id = TEST_PHOTO_ID
        self.serialized_photo = {
            "id": TEST_PHOTO_ID,
            "image_url": TEST_PHOTO_URL,
            "caption": "Updated caption",
            "location": TEST_PHOTO_LOCATION,
        }

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    def test_update_photo_updates_fields(
        self, mock_photo_model, mock_serializer_class, mock_user_model, mock_ws_send
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user_model.objects.all.return_value.values_list.return_value = [1]

        result = PhotoService.update_photo(
            TEST_PHOTO_ID, TEST_ALBUM_ID, {"caption": "Updated caption"}
        )

        mock_serializer.save.assert_called_once()
        self.assertEqual(result, self.serialized_photo)

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    def test_update_photo_broadcasts_update_event(
        self, mock_photo_model, mock_serializer_class, mock_user_model, mock_ws_send
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = self.serialized_photo
        mock_serializer_class.return_value = mock_serializer
        mock_user_model.objects.all.return_value.values_list.return_value = [1, 2, 3]

        PhotoService.update_photo(TEST_PHOTO_ID, TEST_ALBUM_ID, {"caption": "New"})

        # Should broadcast to all 3 users
        assert mock_ws_send.call_count == 3

    @patch("core.services.photo_service.Photo")
    def test_update_photo_raises_not_found_for_nonexistent_photo(
        self, mock_photo_model
    ):
        from rest_framework.exceptions import NotFound

        mock_photo_model.DoesNotExist = Exception
        mock_photo_model.objects.get.side_effect = mock_photo_model.DoesNotExist

        with self.assertRaises(NotFound):
            PhotoService.update_photo(999, TEST_ALBUM_ID, {})


class TestPhotoServiceWebSocketBroadcast(unittest.TestCase):
    """Tests for PhotoService WebSocket broadcast functionality."""

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_save_photo_broadcasts_upload_event(
        self,
        mock_photo_repo,
        mock_album_model,
        mock_serializer_class,
        mock_user_model,
        mock_ws_send,
    ):
        mock_album = MagicMock()
        mock_album.id = TEST_ALBUM_ID
        mock_album_model.objects.get.return_value = mock_album
        mock_photo_repo.save_within_folder.return_value = TEST_PHOTO_URL

        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {"id": 1, "image_url": TEST_PHOTO_URL}
        mock_serializer_class.return_value = mock_serializer

        mock_user_model.objects.all.return_value.values_list.return_value = [1, 2]

        mock_request = MagicMock()
        mock_request.data = MagicMock()
        mock_request.data.copy.return_value = {"caption": "Test"}
        mock_request.FILES = {}

        PhotoService.save_photo(TEST_ALBUM_ID, mock_request)

        # Should broadcast to all users
        assert mock_ws_send.call_count == 2


class TestPhotoServiceMovePhoto(unittest.TestCase):
    """Tests for PhotoService.move_photo_to_album method."""

    def setUp(self):
        self.mock_photo = MagicMock()
        self.mock_photo.id = TEST_PHOTO_ID
        self.mock_photo.album_id = TEST_ALBUM_ID
        self.mock_photo.image_url = TEST_PHOTO_URL

        self.mock_target_album = MagicMock()
        self.mock_target_album.id = 2

        self.mock_user = MagicMock()

        self.serialized_photo = {
            "id": TEST_PHOTO_ID,
            "image_url": TEST_PHOTO_URL,
            "caption": TEST_PHOTO_CAPTION,
            "location": TEST_PHOTO_LOCATION,
        }

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    def test_move_photo_updates_album_fk(
        self, mock_photo_model, mock_album_model, mock_serializer_class,
        mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1]

        PhotoService.move_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        self.assertEqual(self.mock_photo.album, self.mock_target_album)
        self.mock_photo.save.assert_called_once()

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    def test_move_photo_returns_serialized_data(
        self, mock_photo_model, mock_album_model, mock_serializer_class,
        mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1]

        result = PhotoService.move_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        self.assertEqual(result, self.serialized_photo)

    @patch("core.services.photo_service.Photo")
    def test_move_photo_raises_not_found_for_nonexistent_photo(self, mock_photo_model):
        from rest_framework.exceptions import NotFound

        mock_photo_model.DoesNotExist = Exception
        mock_photo_model.objects.get.side_effect = mock_photo_model.DoesNotExist

        with self.assertRaises(NotFound):
            PhotoService.move_photo_to_album(999, 2, MagicMock())

    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    def test_move_photo_raises_not_found_for_nonexistent_target_album(
        self, mock_photo_model, mock_album_model,
    ):
        from rest_framework.exceptions import NotFound

        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.DoesNotExist = Exception
        mock_album_model.objects.get.side_effect = mock_album_model.DoesNotExist

        with self.assertRaises(NotFound):
            PhotoService.move_photo_to_album(TEST_PHOTO_ID, 999, MagicMock())

    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    def test_move_photo_to_same_album_raises_validation_error(
        self, mock_photo_model, mock_album_model,
    ):
        from rest_framework.exceptions import ValidationError

        self.mock_photo.album_id = TEST_ALBUM_ID
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = MagicMock(id=TEST_ALBUM_ID)

        with self.assertRaises(ValidationError):
            PhotoService.move_photo_to_album(
                TEST_PHOTO_ID, TEST_ALBUM_ID, MagicMock()
            )

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    def test_move_photo_broadcasts_moved_event(
        self, mock_photo_model, mock_album_model, mock_serializer_class,
        mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1, 2]

        PhotoService.move_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        assert mock_ws_send.call_count == 2


class TestPhotoServiceCopyPhoto(unittest.TestCase):
    """Tests for PhotoService.copy_photo_to_album method."""

    def setUp(self):
        self.mock_photo = MagicMock()
        self.mock_photo.id = TEST_PHOTO_ID
        self.mock_photo.album_id = TEST_ALBUM_ID
        self.mock_photo.image_url = TEST_PHOTO_URL
        self.mock_photo.caption = TEST_PHOTO_CAPTION
        self.mock_photo.location = TEST_PHOTO_LOCATION

        self.mock_target_album = MagicMock()
        self.mock_target_album.id = 2

        self.mock_user = MagicMock()

        self.new_photo_url = "https://bucket.s3.amazonaws.com/2/copy_photo.jpg"
        self.serialized_photo = {
            "id": 2,
            "image_url": self.new_photo_url,
            "caption": TEST_PHOTO_CAPTION,
            "location": TEST_PHOTO_LOCATION,
        }

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_copy_photo_calls_s3_copy(
        self, mock_photo_repo, mock_album_model, mock_photo_model,
        mock_serializer_class, mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_photo_repo.copy_file.return_value = self.new_photo_url
        mock_new_photo = MagicMock()
        mock_photo_model.objects.create.return_value = mock_new_photo
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1]

        PhotoService.copy_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        mock_photo_repo.copy_file.assert_called_once_with(TEST_PHOTO_URL, 2)

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_copy_photo_creates_new_photo_entry(
        self, mock_photo_repo, mock_album_model, mock_photo_model,
        mock_serializer_class, mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_photo_repo.copy_file.return_value = self.new_photo_url
        mock_new_photo = MagicMock()
        mock_photo_model.objects.create.return_value = mock_new_photo
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1]

        PhotoService.copy_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        mock_photo_model.objects.create.assert_called_once_with(
            album=self.mock_target_album,
            image_url=self.new_photo_url,
            caption=TEST_PHOTO_CAPTION,
            location=TEST_PHOTO_LOCATION,
        )

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_copy_photo_returns_serialized_data(
        self, mock_photo_repo, mock_album_model, mock_photo_model,
        mock_serializer_class, mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_photo_repo.copy_file.return_value = self.new_photo_url
        mock_new_photo = MagicMock()
        mock_photo_model.objects.create.return_value = mock_new_photo
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1]

        result = PhotoService.copy_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        self.assertEqual(result, self.serialized_photo)

    @patch("core.services.photo_service.Photo")
    def test_copy_photo_raises_not_found_for_nonexistent_photo(self, mock_photo_model):
        from rest_framework.exceptions import NotFound

        mock_photo_model.DoesNotExist = Exception
        mock_photo_model.objects.get.side_effect = mock_photo_model.DoesNotExist

        with self.assertRaises(NotFound):
            PhotoService.copy_photo_to_album(999, 2, MagicMock())

    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    def test_copy_photo_raises_not_found_for_nonexistent_target_album(
        self, mock_photo_model, mock_album_model,
    ):
        from rest_framework.exceptions import NotFound

        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.DoesNotExist = Exception
        mock_album_model.objects.get.side_effect = mock_album_model.DoesNotExist

        with self.assertRaises(NotFound):
            PhotoService.copy_photo_to_album(TEST_PHOTO_ID, 999, MagicMock())

    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.Photo")
    @patch("core.services.photo_service.photo_repository")
    def test_copy_photo_s3_failure_raises_error(
        self, mock_photo_repo, mock_photo_model, mock_album_model,
    ):
        from core.exceptions.exceptions import CloudUploadError

        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_photo_repo.copy_file.side_effect = CloudUploadError("S3 copy failed")

        with self.assertRaises(CloudUploadError):
            PhotoService.copy_photo_to_album(TEST_PHOTO_ID, 2, MagicMock())

    @patch("core.services.photo_service.send_ws_message_to_user")
    @patch("core.services.photo_service.User")
    @patch("core.services.photo_service.PhotoSerializer")
    @patch("core.services.photo_service.Photo")
    @patch("core.services.photo_service.Album")
    @patch("core.services.photo_service.photo_repository")
    def test_copy_photo_broadcasts_copied_event(
        self, mock_photo_repo, mock_album_model, mock_photo_model,
        mock_serializer_class, mock_user_model, mock_ws_send,
    ):
        mock_photo_model.objects.get.return_value = self.mock_photo
        mock_album_model.objects.get.return_value = self.mock_target_album
        mock_photo_repo.copy_file.return_value = self.new_photo_url
        mock_new_photo = MagicMock()
        mock_photo_model.objects.create.return_value = mock_new_photo
        mock_serializer_class.return_value.data = self.serialized_photo
        mock_user_model.objects.all.return_value.values_list.return_value = [1, 2]

        PhotoService.copy_photo_to_album(TEST_PHOTO_ID, 2, self.mock_user)

        assert mock_ws_send.call_count == 2


if __name__ == "__main__":
    unittest.main()
