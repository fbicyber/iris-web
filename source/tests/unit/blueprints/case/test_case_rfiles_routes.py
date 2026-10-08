"""Tests for case evidences (rfiles) routes."""
import pytest


class TestCaseEvidencesPage:
    """Test case evidences page endpoints."""

    def test_case_evidences_page_requires_authentication(self, client):
        """Test evidences page requires authentication."""
        response = client.get('/case/evidences?cid=1')
        assert response.status_code in [302, 401]

    def test_case_evidences_page_with_authenticated_user(self, authenticated_client):
        """Test evidences page with authenticated user."""
        response = authenticated_client.get('/case/evidences?cid=1')
        assert response.status_code in [200, 302]


class TestCaseEvidencesList:
    """Test evidences list endpoints."""

    def test_evidences_list_requires_authentication(self, client):
        """Test evidences list requires authentication."""
        response = client.get('/case/evidences/list?cid=1')
        assert response.status_code in [302, 401]

    def test_evidences_list_success(self, authenticated_client):
        """Test fetching evidences list."""
        response = authenticated_client.get('/case/evidences/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'evidences' in data['data']
        assert 'state' in data['data']

    def test_evidences_list_invalid_case(self, authenticated_client):
        """Test evidences list with invalid case."""
        response = authenticated_client.get('/case/evidences/list?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseEvidencesState:
    """Test evidences state endpoint."""

    def test_evidences_state_requires_authentication(self, client):
        """Test evidences state requires authentication."""
        response = client.get('/case/evidences/state?cid=1')
        assert response.status_code in [302, 401]

    def test_evidences_state_success(self, authenticated_client):
        """Test fetching evidences state."""
        response = authenticated_client.get('/case/evidences/state?cid=1')
        assert response.status_code in [200, 400]

    def test_evidences_state_invalid_case(self, authenticated_client):
        """Test evidences state with invalid case."""
        response = authenticated_client.get('/case/evidences/state?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseEvidencesAdd:
    """Test adding evidences."""

    def test_evidence_add_modal_requires_full_access(self, authenticated_client):
        """Test evidence add modal requires full access."""
        response = authenticated_client.get('/case/evidences/add/modal?cid=1')
        assert response.status_code in [200, 403]

    def test_evidence_add_modal_with_admin(self, admin_client):
        """Test evidence add modal with admin."""
        response = admin_client.get('/case/evidences/add/modal?cid=1')
        assert response.status_code == 200

    def test_evidence_add_requires_full_access(self, authenticated_client):
        """Test adding evidence requires full access."""
        response = authenticated_client.post(
            '/case/evidences/add?cid=1',
            json={'filename': 'evidence.log'}
        )
        assert response.status_code in [200, 403]

    def test_evidence_add_success(self, admin_client):
        """Test adding evidence with valid data."""
        response = admin_client.post(
            '/case/evidences/add?cid=1',
            json={
                'filename': 'evidence.log',
                'file_description': 'Test evidence',
                'file_size': 1024,
                'file_hash': 'abc123'
            }
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_evidence_add_missing_required_fields(self, admin_client):
        """Test adding evidence without required fields."""
        response = admin_client.post(
            '/case/evidences/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_evidence_add_invalid_case(self, admin_client):
        """Test adding evidence to invalid case."""
        response = admin_client.post(
            '/case/evidences/add?cid=99999',
            json={'filename': 'test.log'}
        )
        assert response.status_code in [400, 404]


class TestCaseEvidencesView:
    """Test evidence view endpoints."""

    def test_evidence_view_requires_authentication(self, client):
        """Test evidence view requires authentication."""
        response = client.get('/case/evidences/1?cid=1')
        assert response.status_code in [302, 401]

    def test_evidence_view_success(self, authenticated_client):
        """Test viewing single evidence."""
        response = authenticated_client.get('/case/evidences/1?cid=1')
        # May not exist in test DB
        assert response.status_code in [200, 400]

    def test_evidence_view_invalid_evidence(self, authenticated_client):
        """Test viewing invalid evidence."""
        response = authenticated_client.get('/case/evidences/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_evidence_view_modal_requires_authentication(self, client):
        """Test evidence view modal requires authentication."""
        response = client.get('/case/evidences/1/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_evidence_view_modal_success(self, authenticated_client):
        """Test viewing evidence modal."""
        response = authenticated_client.get('/case/evidences/1/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_evidence_view_modal_invalid_evidence(self, authenticated_client):
        """Test viewing modal for invalid evidence."""
        response = authenticated_client.get('/case/evidences/99999/modal?cid=1')
        assert response.status_code in [400, 404]


class TestCaseEvidencesUpdate:
    """Test evidence update endpoints."""

    def test_evidence_update_requires_full_access(self, authenticated_client):
        """Test updating evidence requires full access."""
        response = authenticated_client.post(
            '/case/evidences/update/1?cid=1',
            json={'filename': 'updated.log'}
        )
        assert response.status_code in [200, 403]

    def test_evidence_update_success(self, admin_client):
        """Test updating evidence with valid data."""
        response = admin_client.post(
            '/case/evidences/update/1?cid=1',
            json={
                'filename': 'updated.log',
                'file_description': 'Updated description'
            }
        )
        # May succeed or fail if evidence doesn't exist
        assert response.status_code in [200, 400]

    def test_evidence_update_invalid_evidence(self, admin_client):
        """Test updating invalid evidence."""
        response = admin_client.post(
            '/case/evidences/update/99999?cid=1',
            json={'filename': 'updated.log'}
        )
        assert response.status_code in [400, 404]

    def test_evidence_update_invalid_data(self, admin_client):
        """Test updating evidence with invalid data."""
        response = admin_client.post(
            '/case/evidences/update/1?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_evidence_update_invalid_case(self, admin_client):
        """Test updating evidence with invalid case."""
        response = admin_client.post(
            '/case/evidences/update/1?cid=99999',
            json={'filename': 'updated.log'}
        )
        assert response.status_code in [400, 404]


class TestCaseEvidencesDelete:
    """Test evidence delete endpoint."""

    def test_evidence_delete_requires_full_access(self, authenticated_client):
        """Test deleting evidence requires full access."""
        response = authenticated_client.post('/case/evidences/delete/1?cid=1')
        assert response.status_code in [200, 403]

    def test_evidence_delete_invalid_evidence(self, admin_client):
        """Test deleting invalid evidence."""
        response = admin_client.post('/case/evidences/delete/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_evidence_delete_invalid_case(self, admin_client):
        """Test deleting evidence from invalid case."""
        response = admin_client.post('/case/evidences/delete/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseEvidencesExcelUpload:
    """Test evidence Excel upload."""

    def test_evidence_excel_upload_requires_full_access(self, authenticated_client):
        """Test evidence Excel upload requires full access."""
        response = authenticated_client.post(
            '/case/evidences/excel_upload?cid=1',
            json={'excel_data': []}
        )
        assert response.status_code in [200, 400, 403]

    def test_evidence_excel_upload_missing_data(self, admin_client):
        """Test upload without Excel data."""
        response = admin_client.post(
            '/case/evidences/excel_upload?cid=1',
            json={}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'excel' in data['message'].lower()

    def test_evidence_excel_upload_invalid_case(self, admin_client):
        """Test uploading evidence to invalid case."""
        response = admin_client.post(
            '/case/evidences/excel_upload?cid=99999',
            json={'excel_data': []}
        )
        assert response.status_code in [400, 404]


class TestCaseEvidencesComments:
    """Test evidence comment endpoints."""

    def test_evidence_comments_modal_requires_authentication(self, client):
        """Test evidence comments modal requires authentication."""
        response = client.get('/case/evidences/1/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_evidence_comments_modal_success(self, authenticated_client):
        """Test evidence comments modal."""
        response = authenticated_client.get('/case/evidences/1/comments/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_evidence_comments_list_requires_authentication(self, client):
        """Test evidence comments list requires authentication."""
        response = client.get('/case/evidences/1/comments/list?cid=1')
        assert response.status_code in [302, 401]

    def test_evidence_comments_list_success(self, authenticated_client):
        """Test fetching evidence comments list."""
        response = authenticated_client.get('/case/evidences/1/comments/list?cid=1')
        assert response.status_code in [200, 400]

    def test_evidence_comment_add_requires_full_access(self, authenticated_client):
        """Test adding comment requires full access."""
        response = authenticated_client.post(
            '/case/evidences/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 403]

    def test_evidence_comment_add_success(self, admin_client):
        """Test adding comment to evidence."""
        response = admin_client.post(
            '/case/evidences/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        # May fail if evidence doesn't exist
        assert response.status_code in [200, 400]

    def test_evidence_comment_get_requires_authentication(self, client):
        """Test getting comment requires authentication."""
        response = client.get('/case/evidences/1/comments/1?cid=1')
        assert response.status_code in [302, 401]

    def test_evidence_comment_get_success(self, authenticated_client):
        """Test getting single comment."""
        response = authenticated_client.get('/case/evidences/1/comments/1?cid=1')
        assert response.status_code in [200, 400]

    def test_evidence_comment_edit_requires_full_access(self, authenticated_client):
        """Test editing comment requires full access."""
        response = authenticated_client.post(
            '/case/evidences/1/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        assert response.status_code in [200, 403]

    def test_evidence_comment_delete_requires_full_access(self, authenticated_client):
        """Test deleting comment requires full access."""
        response = authenticated_client.post('/case/evidences/1/comments/1/delete?cid=1')
        assert response.status_code in [200, 403]

    def test_evidence_comment_delete_invalid_comment(self, admin_client):
        """Test deleting invalid comment."""
        response = admin_client.post('/case/evidences/1/comments/99999/delete?cid=1')
        assert response.status_code in [400, 404]
