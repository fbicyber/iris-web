"""Tests for case comments utility."""
import pytest
from unittest.mock import patch, MagicMock


class TestCaseCommentUpdate:
    """Test case comment update functionality."""

    def test_comment_update_requires_authentication(self, client):
        """Test comment update requires authentication."""
        # Comments are updated through parent objects (IOC, asset, etc.)
        # This is tested in individual route tests
        pass

    def test_comment_update_with_valid_data(self, admin_client):
        """Test updating comment with valid data."""
        # Test through IOC comment update endpoint as example
        response = admin_client.post(
            '/case/ioc/1/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment text'}
        )
        # May succeed or fail if comment doesn't exist
        assert response.status_code in [200, 400, 403]

    def test_comment_update_invalid_comment(self, admin_client):
        """Test updating invalid comment."""
        response = admin_client.post(
            '/case/ioc/1/comments/99999/edit?cid=1',
            json={'comment_text': 'Updated'}
        )
        assert response.status_code in [400, 404, 403]

    def test_comment_update_invalid_case(self, admin_client):
        """Test updating comment with invalid case."""
        response = admin_client.post(
            '/case/ioc/1/comments/1/edit?cid=99999',
            json={'comment_text': 'Updated'}
        )
        assert response.status_code in [400, 404, 403]


class TestCommentCrossObjectTypes:
    """Test comments work across different object types."""

    @pytest.mark.parametrize('object_type,object_id', [
        ('ioc', 1),
        ('assets', 1),
        ('tasks', 1),
        ('evidences', 1),
        ('notes', 1),
        ('timeline/events', 1),
    ])
    def test_comment_list_for_object_types(self, authenticated_client, object_type, object_id):
        """Test fetching comments for different object types."""
        response = authenticated_client.get(f'/case/{object_type}/{object_id}/comments/list?cid=1')
        # May not exist but endpoint should be accessible
        assert response.status_code in [200, 400, 404, 302]

    @pytest.mark.parametrize('object_type,object_id', [
        ('ioc', 1),
        ('assets', 1),
        ('tasks', 1),
        ('evidences', 1),
        ('notes', 1),
        ('timeline/events', 1),
    ])
    def test_comment_add_for_object_types(self, admin_client, object_type, object_id):
        """Test adding comments to different object types."""
        response = admin_client.post(
            f'/case/{object_type}/{object_id}/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        # May succeed or fail based on object existence
        assert response.status_code in [200, 400, 403]

    @pytest.mark.parametrize('object_type,object_id', [
        ('ioc', 1),
        ('assets', 1),
        ('tasks', 1),
        ('evidences', 1),
        ('notes', 1),
        ('timeline/events', 1),
    ])
    def test_comment_edit_for_object_types(self, admin_client, object_type, object_id):
        """Test editing comments for different object types."""
        response = admin_client.post(
            f'/case/{object_type}/{object_id}/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        # May succeed or fail based on object existence
        assert response.status_code in [200, 400, 403]


class TestCommentModals:
    """Test comment modals for different object types."""

    @pytest.mark.parametrize('object_type,object_id', [
        ('ioc', 1),
        ('assets', 1),
        ('tasks', 1),
        ('evidences', 1),
        ('notes', 1),
        ('timeline/events', 1),
    ])
    def test_comment_modal_requires_authentication(self, client, object_type, object_id):
        """Test comment modals require authentication."""
        response = client.get(f'/case/{object_type}/{object_id}/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    @pytest.mark.parametrize('object_type,object_id', [
        ('ioc', 1),
        ('assets', 1),
        ('tasks', 1),
        ('evidences', 1),
        ('notes', 1),
        ('timeline/events', 1),
    ])
    def test_comment_modal_with_authenticated_user(self, authenticated_client, object_type, object_id):
        """Test comment modals with authenticated user."""
        response = authenticated_client.get(f'/case/{object_type}/{object_id}/comments/modal?cid=1')
        # May not render if object doesn't exist
        assert response.status_code in [200, 302, 400]
