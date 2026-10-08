"""Tests for case graphs routes."""
import pytest


class TestCaseGraphPage:
    """Test case graph page endpoints."""

    def test_case_graph_page_requires_authentication(self, client):
        """Test graph page requires authentication."""
        response = client.get('/case/graph?cid=1')
        assert response.status_code in [302, 401]

    def test_case_graph_page_with_authenticated_user(self, authenticated_client):
        """Test graph page with authenticated user."""
        response = authenticated_client.get('/case/graph?cid=1')
        assert response.status_code in [200, 302]

    def test_case_graph_page_invalid_case(self, authenticated_client):
        """Test graph page with invalid case."""
        response = authenticated_client.get('/case/graph?cid=99999')
        assert response.status_code in [400, 404, 302]


class TestCaseGraphData:
    """Test case graph data endpoint."""

    def test_graph_data_requires_authentication(self, client):
        """Test graph data requires authentication."""
        response = client.get('/case/graph/getdata?cid=1')
        assert response.status_code in [302, 401]

    def test_graph_data_success(self, authenticated_client):
        """Test fetching graph data."""
        response = authenticated_client.get('/case/graph/getdata?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'nodes' in data['data']
        assert 'edges' in data['data']
        assert 'dates' in data['data']
        assert isinstance(data['data']['nodes'], list)
        assert isinstance(data['data']['edges'], list)

    def test_graph_data_structure(self, authenticated_client):
        """Test graph data has correct structure."""
        response = authenticated_client.get('/case/graph/getdata?cid=1')
        assert response.status_code == 200
        data = response.get_json()

        # Verify dates structure
        assert 'human' in data['data']['dates']
        assert 'machine' in data['data']['dates']
        assert isinstance(data['data']['dates']['human'], list)
        assert isinstance(data['data']['dates']['machine'], list)

    def test_graph_data_invalid_case(self, authenticated_client):
        """Test graph data with invalid case."""
        response = authenticated_client.get('/case/graph/getdata?cid=99999')
        assert response.status_code in [400, 404]

    def test_graph_data_empty_case(self, authenticated_client):
        """Test graph data for case with no events."""
        response = authenticated_client.get('/case/graph/getdata?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        # Empty case should still return valid structure
        assert 'nodes' in data['data']
        assert 'edges' in data['data']
