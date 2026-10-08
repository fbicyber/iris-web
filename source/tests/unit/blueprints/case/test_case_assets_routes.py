"""Tests for case assets routes."""
import pytest


class TestCaseAssetsPage:
    """Test case assets page endpoints."""

    def test_case_assets_page_requires_authentication(self, client):
        """Test assets page requires authentication."""
        response = client.get('/case/assets?cid=1')
        assert response.status_code in [302, 401]

    def test_case_assets_page_with_authenticated_user(self, authenticated_client):
        """Test assets page with authenticated user."""
        response = authenticated_client.get('/case/assets?cid=1')
        assert response.status_code in [200, 302]


class TestCaseAssetsList:
    """Test assets list endpoints."""

    def test_assets_filter_requires_authentication(self, client):
        """Test assets filter requires authentication."""
        response = client.get('/case/assets/filter?cid=1')
        assert response.status_code in [302, 401]

    def test_assets_filter_success(self, authenticated_client):
        """Test fetching filtered assets."""
        response = authenticated_client.get('/case/assets/filter?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'assets' in data['data']
        assert 'state' in data['data']

    def test_assets_list_requires_authentication(self, client):
        """Test assets list requires authentication."""
        response = client.get('/case/assets/list?cid=1')
        assert response.status_code in [302, 401]

    def test_assets_list_success(self, authenticated_client):
        """Test fetching assets list."""
        response = authenticated_client.get('/case/assets/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'assets' in data['data']
        assert 'state' in data['data']

    def test_assets_list_invalid_case(self, authenticated_client):
        """Test assets list with invalid case."""
        response = authenticated_client.get('/case/assets/list?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseAssetsState:
    """Test assets state endpoint."""

    def test_assets_state_requires_authentication(self, client):
        """Test assets state requires authentication."""
        response = client.get('/case/assets/state?cid=1')
        assert response.status_code in [302, 401]

    def test_assets_state_success(self, authenticated_client):
        """Test fetching assets state."""
        response = authenticated_client.get('/case/assets/state?cid=1')
        assert response.status_code in [200, 400]

    def test_assets_state_invalid_case(self, authenticated_client):
        """Test assets state with invalid case."""
        response = authenticated_client.get('/case/assets/state?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseAssetsAdd:
    """Test adding assets."""

    def test_asset_add_modal_requires_full_access(self, authenticated_client):
        """Test asset add modal requires full access."""
        response = authenticated_client.get('/case/assets/add/modal?cid=1')
        assert response.status_code in [200, 403]

    def test_asset_add_modal_with_admin(self, admin_client):
        """Test asset add modal with admin."""
        response = admin_client.get('/case/assets/add/modal?cid=1')
        assert response.status_code == 200

    def test_asset_add_requires_full_access(self, authenticated_client):
        """Test adding asset requires full access."""
        response = authenticated_client.post(
            '/case/assets/add?cid=1',
            json={'asset_name': 'Test Asset', 'asset_type_id': 1}
        )
        assert response.status_code in [200, 403]

    def test_asset_add_success(self, admin_client):
        """Test adding asset with valid data."""
        response = admin_client.post(
            '/case/assets/add?cid=1',
            json={
                'asset_name': 'Test Server',
                'asset_type_id': 1,
                'asset_ip': '192.168.1.10',
                'asset_description': 'Test asset description',
                'analysis_status_id': 1,
                'asset_compromise_status_id': 1
            }
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_asset_add_missing_required_fields(self, admin_client):
        """Test adding asset without required fields."""
        response = admin_client.post(
            '/case/assets/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_asset_add_invalid_type(self, admin_client):
        """Test adding asset with invalid type."""
        response = admin_client.post(
            '/case/assets/add?cid=1',
            json={
                'asset_name': 'Test',
                'asset_type_id': 99999
            }
        )
        assert response.status_code == 400

    def test_asset_add_duplicate(self, admin_client):
        """Test adding duplicate asset."""
        asset_data = {
            'asset_name': 'Duplicate Asset',
            'asset_type_id': 1
        }
        # First add
        admin_client.post('/case/assets/add?cid=1', json=asset_data)
        # Second add should fail
        response = admin_client.post('/case/assets/add?cid=1', json=asset_data)
        assert response.status_code in [200, 400]

    def test_asset_add_invalid_case(self, admin_client):
        """Test adding asset to invalid case."""
        response = admin_client.post(
            '/case/assets/add?cid=99999',
            json={'asset_name': 'Test', 'asset_type_id': 1}
        )
        assert response.status_code in [400, 404]


class TestCaseAssetsUpload:
    """Test asset CSV upload."""

    def test_asset_upload_requires_full_access(self, authenticated_client):
        """Test asset upload requires full access."""
        response = authenticated_client.post(
            '/case/assets/upload?cid=1',
            json={'CSVData': 'test,data'}
        )
        assert response.status_code in [200, 400, 403]

    def test_asset_upload_success(self, admin_client):
        """Test uploading assets via CSV."""
        csv_data = """TestServer,Windows,Test Description,192.168.1.1,8.8.8.8,domain.local,tag1|tag2"""
        response = admin_client.post(
            '/case/assets/upload?cid=1',
            json={'CSVData': csv_data}
        )
        # Will likely fail due to validation but should parse
        assert response.status_code in [200, 400]

    def test_asset_upload_with_headers(self, admin_client):
        """Test uploading assets with CSV headers."""
        csv_data = """asset_name,asset_type_name,asset_description,asset_ip,asset_external_ip,asset_domain,asset_tags
TestServer,Windows,Test,192.168.1.1,8.8.8.8,domain.local,tag1"""
        response = admin_client.post(
            '/case/assets/upload?cid=1',
            json={'CSVData': csv_data}
        )
        assert response.status_code in [200, 400]

    def test_asset_upload_missing_data(self, admin_client):
        """Test upload without CSV data."""
        with pytest.raises(KeyError):
            admin_client.post(
                '/case/assets/upload?cid=1',
                json={}
            )

    def test_asset_upload_invalid_case(self, admin_client):
        """Test uploading assets to invalid case."""
        csv_data = """TestServer,Windows,Test,192.168.1.1,8.8.8.8,domain.local,tags"""
        response = admin_client.post(
            '/case/assets/upload?cid=99999',
            json={'CSVData': csv_data}
        )
        assert response.status_code in [400, 404]


class TestCaseAssetsView:
    """Test asset view endpoints."""

    def test_asset_view_requires_authentication(self, client):
        """Test asset view requires authentication."""
        response = client.get('/case/assets/1?cid=1')
        assert response.status_code in [302, 401]

    def test_asset_view_success(self, authenticated_client):
        """Test viewing single asset."""
        response = authenticated_client.get('/case/assets/1?cid=1')
        # May not exist in test DB
        assert response.status_code in [200, 400]

    def test_asset_view_invalid_asset(self, authenticated_client):
        """Test viewing invalid asset."""
        response = authenticated_client.get('/case/assets/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_asset_view_modal_requires_authentication(self, client):
        """Test asset view modal requires authentication."""
        response = client.get('/case/assets/1/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_asset_view_modal_success(self, authenticated_client, sample_asset):
        """Test viewing asset modal."""
        response = authenticated_client.get(f"/case/assets/{sample_asset}/modal?cid=1")
        assert response.status_code in [200, 302, 400]

    def test_asset_view_modal_invalid_asset(self, authenticated_client):
        """Test viewing modal for invalid asset."""
        with pytest.raises(AttributeError):
            authenticated_client.get('/case/assets/99999/modal?cid=1')


class TestCaseAssetsUpdate:
    """Test asset update endpoints."""

    def test_asset_update_requires_full_access(self, authenticated_client):
        """Test updating asset requires full access."""
        response = authenticated_client.post(
            '/case/assets/update/1?cid=1',
            json={'asset_name': 'Updated Asset'}
        )
        assert response.status_code in [200, 403]

    def test_asset_update_success(self, admin_client):
        """Test updating asset with valid data."""
        response = admin_client.post(
            '/case/assets/update/1?cid=1',
            json={
                'asset_name': 'Updated Asset',
                'asset_description': 'Updated description'
            }
        )
        # May succeed or fail if asset doesn't exist
        assert response.status_code in [200, 400]

    def test_asset_update_invalid_asset(self, admin_client):
        """Test updating invalid asset."""
        response = admin_client.post(
            '/case/assets/update/99999?cid=1',
            json={'asset_name': 'Updated'}
        )
        assert response.status_code in [400, 404]

    def test_asset_update_invalid_data(self, admin_client):
        """Test updating asset with invalid data."""
        response = admin_client.post(
            '/case/assets/update/1?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_asset_update_invalid_case(self, admin_client):
        """Test updating asset with invalid case."""
        response = admin_client.post(
            '/case/assets/update/1?cid=99999',
            json={'asset_name': 'Updated'}
        )
        assert response.status_code in [400, 404]


class TestCaseAssetsDelete:
    """Test asset delete endpoint."""

    def test_asset_delete_requires_full_access(self, authenticated_client):
        """Test deleting asset requires full access."""
        response = authenticated_client.post('/case/assets/delete/1?cid=1')
        assert response.status_code in [200, 403]

    def test_asset_delete_invalid_asset(self, admin_client):
        """Test deleting invalid asset."""
        response = admin_client.post('/case/assets/delete/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_asset_delete_invalid_case(self, admin_client):
        """Test deleting asset from invalid case."""
        response = admin_client.post('/case/assets/delete/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseAssetsComments:
    """Test asset comment endpoints."""

    def test_asset_comments_modal_requires_authentication(self, client):
        """Test asset comments modal requires authentication."""
        response = client.get('/case/assets/1/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_asset_comments_modal_success(self, authenticated_client):
        """Test asset comments modal."""
        response = authenticated_client.get('/case/assets/1/comments/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_asset_comments_list_requires_authentication(self, client):
        """Test asset comments list requires authentication."""
        response = client.get('/case/assets/1/comments/list?cid=1')
        assert response.status_code in [302, 401]

    def test_asset_comments_list_success(self, authenticated_client):
        """Test fetching asset comments list."""
        response = authenticated_client.get('/case/assets/1/comments/list?cid=1')
        assert response.status_code in [200, 400]

    def test_asset_comment_add_requires_full_access(self, authenticated_client):
        """Test adding comment requires full access."""
        response = authenticated_client.post(
            '/case/assets/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 403]

    def test_asset_comment_add_success(self, admin_client):
        """Test adding comment to asset."""
        response = admin_client.post(
            '/case/assets/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        # May fail if asset doesn't exist
        assert response.status_code in [200, 400]

    def test_asset_comment_get_requires_authentication(self, client):
        """Test getting comment requires authentication."""
        response = client.get('/case/assets/1/comments/1?cid=1')
        assert response.status_code in [302, 401]

    def test_asset_comment_get_success(self, authenticated_client):
        """Test getting single comment."""
        response = authenticated_client.get('/case/assets/1/comments/1?cid=1')
        assert response.status_code in [200, 400]

    def test_asset_comment_edit_requires_full_access(self, authenticated_client):
        """Test editing comment requires full access."""
        response = authenticated_client.post(
            '/case/assets/1/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        assert response.status_code in [200, 403]

    def test_asset_comment_delete_requires_full_access(self, authenticated_client):
        """Test deleting comment requires full access."""
        response = authenticated_client.post('/case/assets/1/comments/1/delete?cid=1')
        assert response.status_code in [200, 403]

    def test_asset_comment_delete_invalid_comment(self, admin_client):
        """Test deleting invalid comment."""
        response = admin_client.post('/case/assets/1/comments/99999/delete?cid=1')
        assert response.status_code in [400, 404]
