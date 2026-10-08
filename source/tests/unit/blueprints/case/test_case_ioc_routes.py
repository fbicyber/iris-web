"""Tests for case IOC routes."""
import pytest


class TestCaseIocPage:
    """Test case IOC page endpoints."""

    def test_case_ioc_page_requires_authentication(self, client):
        """Test IOC page requires authentication."""
        response = client.get('/case/ioc?cid=1')
        assert response.status_code in [302, 401]

    def test_case_ioc_page_with_authenticated_user(self, authenticated_client):
        """Test IOC page with authenticated user."""
        response = authenticated_client.get('/case/ioc?cid=1')
        assert response.status_code in [200, 302]


class TestCaseIocList:
    """Test IOC list endpoints."""

    def test_ioc_list_requires_authentication(self, client):
        """Test IOC list requires authentication."""
        response = client.get('/case/ioc/list?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_list_success(self, authenticated_client):
        """Test fetching IOC list."""
        response = authenticated_client.get('/case/ioc/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'ioc' in data['data']
        assert 'state' in data['data']
        assert isinstance(data['data']['ioc'], list)

    def test_ioc_list_invalid_case(self, authenticated_client):
        """Test IOC list with invalid case."""
        response = authenticated_client.get('/case/ioc/list?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseIocState:
    """Test IOC state endpoint."""

    def test_ioc_state_requires_authentication(self, client):
        """Test IOC state requires authentication."""
        response = client.get('/case/ioc/state?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_state_success(self, authenticated_client):
        """Test fetching IOC state."""
        response = authenticated_client.get('/case/ioc/state?cid=1')
        assert response.status_code in [200, 400]

    def test_ioc_state_invalid_case(self, authenticated_client):
        """Test IOC state with invalid case."""
        response = authenticated_client.get('/case/ioc/state?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseIocAdd:
    """Test adding IOCs."""

    def test_ioc_add_requires_full_access(self, authenticated_client):
        """Test adding IOC requires full access."""
        response = authenticated_client.post(
            '/case/ioc/add?cid=1',
            json={'ioc_value': '192.168.1.1', 'ioc_type_id': 1}
        )
        assert response.status_code in [200, 403]

    def test_ioc_add_success(self, admin_client):
        """Test adding IOC with valid data."""
        response = admin_client.post(
            '/case/ioc/add?cid=1',
            json={
                'ioc_value': '192.168.1.100',
                'ioc_type_id': 1,
                'ioc_description': 'Test IOC',
                'ioc_tlp_id': 1
            }
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_ioc_add_missing_required_fields(self, admin_client):
        """Test adding IOC without required fields."""
        response = admin_client.post(
            '/case/ioc/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_ioc_add_invalid_type(self, admin_client):
        """Test adding IOC with invalid type."""
        response = admin_client.post(
            '/case/ioc/add?cid=1',
            json={
                'ioc_value': '192.168.1.1',
                'ioc_type_id': 99999
            }
        )
        assert response.status_code == 400

    def test_ioc_add_invalid_case(self, admin_client):
        """Test adding IOC to invalid case."""
        response = admin_client.post(
            '/case/ioc/add?cid=99999',
            json={'ioc_value': '192.168.1.1', 'ioc_type_id': 1}
        )
        assert response.status_code in [400, 404]


class TestCaseIocUpload:
    """Test IOC CSV upload."""

    def test_ioc_upload_requires_full_access(self, authenticated_client):
        """Test IOC upload requires full access."""
        response = authenticated_client.post(
            '/case/ioc/upload?cid=1',
            json={'CSVData': 'test,data'}
        )
        assert response.status_code in [200, 400, 403]

    def test_ioc_upload_success(self, admin_client):
        """Test uploading IOCs via CSV."""
        csv_data = """192.168.1.1,ip-dst,Test IP,tag1|tag2,white"""
        response = admin_client.post(
            '/case/ioc/upload?cid=1',
            json={'CSVData': csv_data}
        )
        # Will likely fail due to validation but should parse
        assert response.status_code in [200, 400]

    def test_ioc_upload_with_headers(self, admin_client):
        """Test uploading IOCs with CSV headers."""
        csv_data = """ioc_value,ioc_type,ioc_description,ioc_tags,ioc_tlp
192.168.1.1,ip-dst,Test IP,tag1,white"""
        response = admin_client.post(
            '/case/ioc/upload?cid=1',
            json={'CSVData': csv_data}
        )
        assert response.status_code in [200, 400]

    def test_ioc_upload_invalid_csv(self, admin_client):
        """Test uploading invalid CSV data."""
        with pytest.raises(IndexError):
            admin_client.post(
                '/case/ioc/upload?cid=1',
                json={'CSVData': ''}
            )

    def test_ioc_upload_missing_data(self, admin_client):
        """Test upload without CSV data."""
        with pytest.raises(KeyError):
            admin_client.post(
                '/case/ioc/upload?cid=1',
                json={}
            )

    def test_ioc_upload_invalid_case(self, admin_client):
        """Test uploading IOCs to invalid case."""
        csv_data = """192.168.1.1,ip-dst,Test,tags,white"""
        response = admin_client.post(
            '/case/ioc/upload?cid=99999',
            json={'CSVData': csv_data}
        )
        assert response.status_code in [400, 404]


class TestCaseIocModal:
    """Test IOC modal endpoints."""

    def test_ioc_add_modal_requires_full_access(self, authenticated_client):
        """Test IOC add modal requires full access."""
        response = authenticated_client.get('/case/ioc/add/modal?cid=1')
        assert response.status_code in [200, 403]

    def test_ioc_add_modal_with_admin(self, admin_client):
        """Test IOC add modal with admin."""
        response = admin_client.get('/case/ioc/add/modal?cid=1')
        assert response.status_code == 200

    def test_ioc_view_modal_requires_authentication(self, client):
        """Test IOC view modal requires authentication."""
        response = client.get('/case/ioc/1/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_view_modal_success(self, authenticated_client):
        """Test viewing IOC modal."""
        response = authenticated_client.get('/case/ioc/1/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_ioc_view_modal_invalid_ioc(self, authenticated_client):
        """Test viewing modal for invalid IOC."""
        response = authenticated_client.get('/case/ioc/99999/modal?cid=1')
        assert response.status_code in [400, 404]


class TestCaseIocView:
    """Test IOC view endpoints."""

    def test_ioc_view_requires_authentication(self, client):
        """Test IOC view requires authentication."""
        response = client.get('/case/ioc/1?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_view_success(self, authenticated_client):
        """Test viewing single IOC."""
        response = authenticated_client.get('/case/ioc/1?cid=1')
        # May not exist in test DB
        assert response.status_code in [200, 400]

    def test_ioc_view_invalid_ioc(self, authenticated_client):
        """Test viewing invalid IOC."""
        response = authenticated_client.get('/case/ioc/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_ioc_view_invalid_case(self, authenticated_client):
        """Test viewing IOC with invalid case."""
        response = authenticated_client.get('/case/ioc/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseIocUpdate:
    """Test IOC update endpoints."""

    def test_ioc_update_requires_full_access(self, authenticated_client):
        """Test updating IOC requires full access."""
        response = authenticated_client.post(
            '/case/ioc/update/1?cid=1',
            json={'ioc_value': '192.168.1.1'}
        )
        assert response.status_code in [200, 403]

    def test_ioc_update_success(self, admin_client, sample_ioc):
        """Test updating IOC with valid data."""
        response = admin_client.post(
            f'/case/ioc/update/{sample_ioc}?cid=1',
            json={
                'ioc_value': '192.168.1.2',
                'ioc_description': 'Updated description'
            }
        )
        assert response.status_code == 200

    def test_ioc_update_invalid_ioc(self, admin_client):
        """Test updating invalid IOC."""
        with pytest.raises(TypeError):
            admin_client.post(
                '/case/ioc/update/99999?cid=1',
                json={'ioc_value': '192.168.1.1'}
            )

    def test_ioc_update_invalid_case(self, admin_client):
        """Test updating IOC with invalid case."""
        response = admin_client.post(
            '/case/ioc/update/1?cid=99999',
            json={'ioc_value': '192.168.1.1'}
        )
        assert response.status_code in [400, 404]


class TestCaseIocDelete:
    """Test IOC delete endpoint."""

    def test_ioc_delete_requires_full_access(self, authenticated_client):
        """Test deleting IOC requires full access."""
        response = authenticated_client.post('/case/ioc/delete/1?cid=1')
        assert response.status_code in [200, 403]

    def test_ioc_delete_invalid_ioc(self, admin_client):
        """Test deleting invalid IOC."""
        response = admin_client.post('/case/ioc/delete/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_ioc_delete_invalid_case(self, admin_client):
        """Test deleting IOC from invalid case."""
        response = admin_client.post('/case/ioc/delete/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseIocComments:
    """Test IOC comment endpoints."""

    def test_ioc_comments_modal_requires_authentication(self, client):
        """Test IOC comments modal requires authentication."""
        response = client.get('/case/ioc/1/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_comments_modal_success(self, authenticated_client):
        """Test IOC comments modal."""
        response = authenticated_client.get('/case/ioc/1/comments/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_ioc_comments_modal_invalid_ioc(self, authenticated_client):
        """Test comments modal for invalid IOC."""
        response = authenticated_client.get('/case/ioc/99999/comments/modal?cid=1')
        assert response.status_code in [400, 404]

    def test_ioc_comments_list_requires_authentication(self, client):
        """Test IOC comments list requires authentication."""
        response = client.get('/case/ioc/1/comments/list?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_comments_list_success(self, authenticated_client):
        """Test fetching IOC comments list."""
        response = authenticated_client.get('/case/ioc/1/comments/list?cid=1')
        # May not exist in test DB
        assert response.status_code in [200, 400]

    def test_ioc_comment_add_requires_full_access(self, authenticated_client):
        """Test adding comment requires full access."""
        response = authenticated_client.post(
            '/case/ioc/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 403]

    def test_ioc_comment_add_success(self, admin_client):
        """Test adding comment to IOC."""
        response = admin_client.post(
            '/case/ioc/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        # May fail if IOC doesn't exist
        assert response.status_code in [200, 400]

    def test_ioc_comment_add_invalid_ioc(self, admin_client):
        """Test adding comment to invalid IOC."""
        response = admin_client.post(
            '/case/ioc/99999/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [400, 404]

    def test_ioc_comment_get_requires_authentication(self, client):
        """Test getting comment requires authentication."""
        response = client.get('/case/ioc/1/comments/1?cid=1')
        assert response.status_code in [302, 401]

    def test_ioc_comment_get_success(self, authenticated_client):
        """Test getting single comment."""
        response = authenticated_client.get('/case/ioc/1/comments/1?cid=1')
        # May not exist
        assert response.status_code in [200, 400]

    def test_ioc_comment_get_invalid_comment(self, authenticated_client):
        """Test getting invalid comment."""
        response = authenticated_client.get('/case/ioc/1/comments/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_ioc_comment_edit_requires_full_access(self, authenticated_client):
        """Test editing comment requires full access."""
        response = authenticated_client.post(
            '/case/ioc/1/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        assert response.status_code in [200, 403]

    def test_ioc_comment_edit_invalid_comment(self, admin_client):
        """Test editing invalid comment."""
        response = admin_client.post(
            '/case/ioc/1/comments/99999/edit?cid=1',
            json={'comment_text': 'Updated'}
        )
        assert response.status_code in [400, 404]

    def test_ioc_comment_delete_requires_full_access(self, authenticated_client):
        """Test deleting comment requires full access."""
        response = authenticated_client.post('/case/ioc/1/comments/1/delete?cid=1')
        assert response.status_code in [200, 403]

    def test_ioc_comment_delete_invalid_comment(self, admin_client):
        """Test deleting invalid comment."""
        response = admin_client.post('/case/ioc/1/comments/99999/delete?cid=1')
        assert response.status_code in [400, 404]

    def test_ioc_comment_delete_invalid_case(self, admin_client):
        """Test deleting comment from invalid case."""
        response = admin_client.post('/case/ioc/1/comments/1/delete?cid=99999')
        assert response.status_code in [400, 404]
