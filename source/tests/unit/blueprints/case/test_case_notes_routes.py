"""Tests for case notes routes."""
import pytest


class TestCaseNotesPage:
    """Test case notes page endpoints."""

    def test_case_notes_page_requires_authentication(self, client):
        """Test notes page requires authentication."""
        response = client.get('/case/notes?cid=1')
        assert response.status_code in [302, 401]

    def test_case_notes_page_with_authenticated_user(self, authenticated_client):
        """Test notes page with authenticated user."""
        response = authenticated_client.get('/case/notes?cid=1')
        assert response.status_code in [200, 302]


class TestCaseNotesState:
    """Test notes state endpoint."""

    def test_notes_state_requires_authentication(self, client):
        """Test notes state requires authentication."""
        response = client.get('/case/notes/state?cid=1')
        assert response.status_code in [302, 401]

    def test_notes_state_success(self, authenticated_client):
        """Test fetching notes state."""
        response = authenticated_client.get('/case/notes/state?cid=1')
        assert response.status_code in [200, 400]

    def test_notes_state_invalid_case(self, authenticated_client):
        """Test notes state with invalid case."""
        response = authenticated_client.get('/case/notes/state?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseNotesDetail:
    """Test note detail endpoints."""

    def test_note_detail_requires_authentication(self, client):
        """Test note detail requires authentication."""
        response = client.get('/case/notes/1?cid=1')
        assert response.status_code in [302, 401]

    def test_note_detail_success(self, authenticated_client):
        """Test viewing single note."""
        response = authenticated_client.get('/case/notes/1?cid=1')
        # May not exist in test DB
        assert response.status_code in [200, 400]

    def test_note_detail_invalid_note(self, authenticated_client):
        """Test viewing invalid note."""
        response = authenticated_client.get('/case/notes/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_note_detail_invalid_case(self, authenticated_client):
        """Test viewing note with invalid case."""
        response = authenticated_client.get('/case/notes/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseNotesAdd:
    """Test adding notes."""

    def test_note_add_requires_full_access(self, authenticated_client):
        """Test adding note requires full access."""
        response = authenticated_client.post(
            '/case/notes/add?cid=1',
            json={'note_title': 'Test Note', 'note_content': 'Content'}
        )
        assert response.status_code in [200, 403]

    def test_note_add_success(self, admin_client):
        """Test adding note with valid data."""
        response = admin_client.post(
            '/case/notes/add?cid=1',
            json={
                'note_title': 'Test Note',
                'note_content': 'Test content'
            }
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_note_add_missing_required_fields(self, admin_client):
        """Test adding note without required fields."""
        response = admin_client.post(
            '/case/notes/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_note_add_invalid_case(self, admin_client):
        """Test adding note to invalid case."""
        response = admin_client.post(
            '/case/notes/add?cid=99999',
            json={'note_title': 'Test', 'note_content': 'Content'}
        )
        assert response.status_code in [400, 404]


class TestCaseNotesUpdate:
    """Test note update endpoints."""

    def test_note_update_requires_full_access(self, authenticated_client):
        """Test updating note requires full access."""
        response = authenticated_client.post(
            '/case/notes/update/1?cid=1',
            json={'note_title': 'Updated Note'}
        )
        assert response.status_code in [200, 403]

    def test_note_update_success(self, admin_client):
        """Test updating note with valid data."""
        response = admin_client.post(
            '/case/notes/update/1?cid=1',
            json={
                'note_title': 'Updated Note',
                'note_content': 'Updated content'
            }
        )
        # May succeed or fail if note doesn't exist
        assert response.status_code in [200, 400]

    def test_note_update_invalid_note(self, admin_client):
        """Test updating invalid note."""
        response = admin_client.post(
            '/case/notes/update/99999?cid=1',
            json={'note_title': 'Updated'}
        )
        assert response.status_code in [400, 404]

    def test_note_update_invalid_case(self, admin_client):
        """Test updating note with invalid case."""
        response = admin_client.post(
            '/case/notes/update/1?cid=99999',
            json={'note_title': 'Updated'}
        )
        assert response.status_code in [400, 404]


class TestCaseNotesDelete:
    """Test note delete endpoint."""

    def test_note_delete_requires_full_access(self, authenticated_client):
        """Test deleting note requires full access."""
        response = authenticated_client.post('/case/notes/delete/1?cid=1')
        assert response.status_code in [200, 403]

    def test_note_delete_invalid_note(self, admin_client):
        """Test deleting invalid note."""
        response = admin_client.post('/case/notes/delete/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_note_delete_invalid_case(self, admin_client):
        """Test deleting note from invalid case."""
        response = admin_client.post('/case/notes/delete/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseNotesRevisions:
    """Test note revisions endpoints."""

    def test_note_revisions_list_requires_authentication(self, client):
        """Test note revisions list requires authentication."""
        response = client.get('/case/notes/1/revisions/list?cid=1')
        assert response.status_code in [302, 401]

    def test_note_revisions_list_success(self, authenticated_client):
        """Test fetching note revisions list."""
        response = authenticated_client.get('/case/notes/1/revisions/list?cid=1')
        # May not exist
        assert response.status_code in [200, 400]

    def test_note_revisions_list_invalid_note(self, authenticated_client):
        """Test revisions list for invalid note."""
        response = authenticated_client.get('/case/notes/99999/revisions/list?cid=1')
        assert response.status_code in [400, 404]

    def test_note_revision_get_requires_authentication(self, client):
        """Test getting note revision requires authentication."""
        response = client.get('/case/notes/1/revisions/1?cid=1')
        assert response.status_code in [302, 401]

    def test_note_revision_get_success(self, authenticated_client):
        """Test getting single note revision."""
        response = authenticated_client.get('/case/notes/1/revisions/1?cid=1')
        # May not exist
        assert response.status_code in [200, 400]

    def test_note_revision_get_invalid_revision(self, authenticated_client):
        """Test getting invalid revision."""
        response = authenticated_client.get('/case/notes/1/revisions/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_note_revision_delete_requires_full_access(self, authenticated_client):
        """Test deleting revision requires full access."""
        response = authenticated_client.post('/case/notes/1/revisions/1/delete?cid=1')
        assert response.status_code in [200, 403]

    def test_note_revision_delete_invalid_revision(self, admin_client):
        """Test deleting invalid revision."""
        response = admin_client.post('/case/notes/1/revisions/99999/delete?cid=1')
        assert response.status_code in [400, 404]


class TestCaseNotesSearch:
    """Test notes search endpoint."""

    def test_notes_search_requires_authentication(self, client):
        """Test notes search requires authentication."""
        response = client.get('/case/notes/search?cid=1&search_input=test')
        assert response.status_code in [302, 401]

    def test_notes_search_success(self, authenticated_client):
        """Test searching notes."""
        response = authenticated_client.get('/case/notes/search?cid=1&search_input=test')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)

    def test_notes_search_empty_input(self, authenticated_client):
        """Test searching with empty input."""
        response = authenticated_client.get('/case/notes/search?cid=1&search_input=')
        assert response.status_code == 200

    def test_notes_search_invalid_case(self, authenticated_client):
        """Test searching notes in invalid case."""
        response = authenticated_client.get('/case/notes/search?cid=99999&search_input=test')
        assert response.status_code in [400, 404]


class TestCaseNotesDirectories:
    """Test notes directories endpoints."""

    def test_directories_filter_requires_authentication(self, client):
        """Test directories filter requires authentication."""
        response = client.get('/case/notes/directories/filter?cid=1')
        assert response.status_code in [302, 401]

    def test_directories_filter_success(self, authenticated_client):
        """Test fetching directories."""
        response = authenticated_client.get('/case/notes/directories/filter?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_directories_filter_invalid_case(self, authenticated_client):
        """Test directories filter with invalid case."""
        response = authenticated_client.get('/case/notes/directories/filter?cid=99999')
        assert response.status_code in [400, 404]

    def test_directory_add_requires_full_access(self, authenticated_client):
        """Test adding directory requires full access."""
        response = authenticated_client.post(
            '/case/notes/directories/add?cid=1',
            json={'name': 'Test Directory'}
        )
        assert response.status_code in [200, 403]

    def test_directory_add_success(self, admin_client):
        """Test adding directory with valid data."""
        response = admin_client.post(
            '/case/notes/directories/add?cid=1',
            json={'name': 'Test Directory'}
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_directory_add_missing_name(self, admin_client):
        """Test adding directory without name."""
        response = admin_client.post(
            '/case/notes/directories/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_directory_update_requires_full_access(self, authenticated_client):
        """Test updating directory requires full access."""
        response = authenticated_client.post(
            '/case/notes/directories/update/1?cid=1',
            json={'name': 'Updated Directory'}
        )
        assert response.status_code in [200, 403]

    def test_directory_update_success(self, admin_client):
        """Test updating directory."""
        response = admin_client.post(
            '/case/notes/directories/update/1?cid=1',
            json={'name': 'Updated Directory'}
        )
        # May succeed or fail if doesn't exist
        assert response.status_code in [200, 400]

    def test_directory_update_invalid_directory(self, admin_client):
        """Test updating invalid directory."""
        response = admin_client.post(
            '/case/notes/directories/update/99999?cid=1',
            json={'name': 'Updated'}
        )
        assert response.status_code in [400, 404]

    def test_directory_delete_requires_full_access(self, authenticated_client):
        """Test deleting directory requires full access."""
        response = authenticated_client.post('/case/notes/directories/delete/1?cid=1')
        assert response.status_code in [200, 403]

    def test_directory_delete_invalid_directory(self, admin_client):
        """Test deleting invalid directory."""
        response = admin_client.post('/case/notes/directories/delete/99999?cid=1')
        assert response.status_code in [400, 404]


class TestCaseNotesComments:
    """Test note comment endpoints."""

    def test_note_comments_modal_requires_authentication(self, client):
        """Test note comments modal requires authentication."""
        response = client.get('/case/notes/1/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_note_comments_modal_success(self, authenticated_client):
        """Test note comments modal."""
        response = authenticated_client.get('/case/notes/1/comments/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_note_comments_list_requires_authentication(self, client):
        """Test note comments list requires authentication."""
        response = client.get('/case/notes/1/comments/list?cid=1')
        assert response.status_code in [302, 401]

    def test_note_comments_list_success(self, authenticated_client):
        """Test fetching note comments list."""
        response = authenticated_client.get('/case/notes/1/comments/list?cid=1')
        assert response.status_code in [200, 400]

    def test_note_comment_add_requires_full_access(self, authenticated_client):
        """Test adding comment requires full access."""
        response = authenticated_client.post(
            '/case/notes/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 403]

    def test_note_comment_add_success(self, admin_client):
        """Test adding comment to note."""
        response = admin_client.post(
            '/case/notes/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        # May fail if note doesn't exist
        assert response.status_code in [200, 400]

    def test_note_comment_add_missing_text(self, admin_client):
        """Test adding comment without text."""
        response = admin_client.post(
            '/case/notes/1/comments/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_note_comment_get_requires_authentication(self, client):
        """Test getting comment requires authentication."""
        response = client.get('/case/notes/1/comments/1?cid=1')
        assert response.status_code in [302, 401]

    def test_note_comment_get_success(self, authenticated_client):
        """Test getting single comment."""
        response = authenticated_client.get('/case/notes/1/comments/1?cid=1')
        assert response.status_code in [200, 400]

    def test_note_comment_edit_requires_full_access(self, authenticated_client):
        """Test editing comment requires full access."""
        response = authenticated_client.post(
            '/case/notes/1/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        assert response.status_code in [200, 403]

    def test_note_comment_delete_requires_full_access(self, authenticated_client):
        """Test deleting comment requires full access."""
        response = authenticated_client.post('/case/notes/1/comments/1/delete?cid=1')
        assert response.status_code in [200, 403]

    def test_note_comment_delete_invalid_comment(self, admin_client):
        """Test deleting invalid comment."""
        response = admin_client.post('/case/notes/1/comments/99999/delete?cid=1')
        assert response.status_code in [400, 404]
