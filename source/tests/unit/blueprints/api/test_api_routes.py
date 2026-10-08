"""
Example tests demonstrating how to test authenticated API endpoints.
"""
import pytest
import json


def test_api_ping_without_auth_fails(client):
    """Test that API endpoint requires authentication."""
    response = client.get('/api/ping')
    assert response.status_code == 401
    data = response.get_json()
    assert data['status'] == 'error'
    assert 'Authentication required' in data['message']


def test_api_ping_with_authenticated_session(authenticated_client):
    """Test API endpoint with authenticated session."""
    response = authenticated_client.get('/api/ping')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == 'pong'


def test_api_post_with_authenticated_session(authenticated_client, api_headers):
    """Test POST request to API with authenticated session."""
    response = authenticated_client.post(
        '/api/some-endpoint',
        headers=api_headers,
        data=json.dumps({'key': 'value'})
    )
    # Adjust assertions based on your actual endpoint


def test_api_with_admin_permissions(admin_client):
    """Test API endpoint that requires admin permissions."""
    response = admin_client.get('/api/versions')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'


def test_multiple_requests_same_session(authenticated_client):
    """Test that session persists across multiple requests."""
    # First request
    response1 = authenticated_client.get('/api/ping')
    assert response1.status_code == 200

    # Second request - should still be authenticated
    response2 = authenticated_client.get('/api/versions')
    assert response2.status_code == 200


def test_api_with_case_context(authenticated_client):
    """Test API endpoint that requires case context."""
    # The authenticated_client fixture sets up user with ctx_case
    response = authenticated_client.get('/api/ping')
    assert response.status_code == 200

    # You can verify the user has case context
    with authenticated_client.application.app_context():
        from flask_login import current_user
        # Note: current_user is only available within a request context


def test_api_with_custom_headers(authenticated_client):
    """Test adding custom headers to authenticated requests."""
    response = authenticated_client.get('/api/ping', headers={
        'X-Custom-Header': 'value',
        'Accept': 'application/json'
    })
    assert response.status_code == 200


class TestAuthenticatedAPIEndpoints:
    """Group related authenticated API tests in a class."""

    def test_list_endpoint(self, authenticated_client):
        """Test listing resources."""
        response = authenticated_client.get('/api/resources')
        # Adjust based on your actual endpoints
        # assert response.status_code == 200

    def test_create_endpoint(self, authenticated_client, api_headers):
        """Test creating a resource."""
        payload = {'name': 'test resource'}
        response = authenticated_client.post(
            '/api/resources',
            headers=api_headers,
            data=json.dumps(payload)
        )
        # Adjust based on your actual endpoints
        # assert response.status_code == 201

    def test_update_endpoint(self, authenticated_client, api_headers):
        """Test updating a resource."""
        payload = {'name': 'updated name'}
        response = authenticated_client.put(
            '/api/resources/1',
            headers=api_headers,
            data=json.dumps(payload)
        )
        # Adjust based on your actual endpoints

    def test_delete_endpoint(self, authenticated_client):
        """Test deleting a resource."""
        response = authenticated_client.delete('/api/resources/1')
        # Adjust based on your actual endpoints


# Example of parametrized test with authentication
@pytest.mark.parametrize('endpoint', [
    '/api/ping',
    '/api/versions',
])
def test_multiple_endpoints_require_auth(client, endpoint):
    """Test that multiple endpoints require authentication."""
    response = client.get(endpoint)
    assert response.status_code == 401


@pytest.mark.parametrize('endpoint', [
    '/api/ping',
    '/api/versions',
])
def test_multiple_endpoints_with_auth(authenticated_client, endpoint):
    """Test multiple endpoints with authentication."""
    response = authenticated_client.get(endpoint)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
