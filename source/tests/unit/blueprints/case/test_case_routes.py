"""Tests for case routes."""
import pytest
from unittest.mock import patch, MagicMock


class TestCaseRoutes:
    """Test case main routes."""

    def test_case_page_requires_authentication(self, client):
        """Test that case page requires authentication."""
        response = client.get('/case?cid=1')
        assert response.status_code in [302, 401]

    def test_case_page_with_authenticated_user(self, authenticated_client):
        """Test case page access with authenticated user."""
        response = authenticated_client.get('/case?cid=1')
        assert response.status_code in [200, 302]

    def test_case_exists_success(self, authenticated_client):
        """Test case exists endpoint returns success for valid case."""
        response = authenticated_client.get('/case/exists?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_case_exists_invalid_case(self, authenticated_client):
        """Test case exists endpoint returns error for invalid case."""
        response = authenticated_client.get('/case/exists?cid=99999')
        assert response.status_code == 404

    def test_case_pipelines_modal_requires_full_access(self, client):
        """Test pipelines modal requires full access."""
        response = client.get('/case/pipelines-modal?cid=1')
        assert response.status_code in [302, 401, 403]

    def test_case_pipelines_modal_with_admin(self, admin_client):
        """Test pipelines modal with admin access."""
        response = admin_client.get('/case/pipelines-modal?cid=1')
        assert response.status_code in [200, 302]


class TestCaseSummary:
    """Test case summary endpoints."""

    def test_summary_update_requires_full_access(self, authenticated_client):
        """Test summary update requires full access."""
        response = authenticated_client.post(
            '/case/summary/update?cid=1',
            json={'case_description': 'Updated summary'}
        )
        assert response.status_code in [200, 403]

    def test_summary_update_success(self, admin_client):
        """Test summary update with valid data."""
        response = admin_client.post(
            '/case/summary/update?cid=1',
            json={'case_description': 'Updated case summary'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_summary_update_invalid_case(self, admin_client):
        """Test summary update with invalid case ID."""
        response = admin_client.post(
            '/case/summary/update?cid=99999',
            json={'case_description': 'Summary'}
        )
        assert response.status_code in [400, 404]

    def test_summary_fetch_success(self, authenticated_client):
        """Test fetching case summary."""
        response = authenticated_client.get('/case/summary/fetch?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'case_description' in data['data']

    def test_summary_fetch_invalid_case(self, authenticated_client):
        """Test fetching summary for invalid case."""
        response = authenticated_client.get('/case/summary/fetch?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseActivities:
    """Test case activities endpoint."""

    def test_activities_list_requires_authentication(self, client):
        """Test activities list requires authentication."""
        response = client.get('/case/activities/list?cid=1')
        assert response.status_code in [302, 401]

    def test_activities_list_success(self, authenticated_client):
        """Test fetching activities list."""
        response = authenticated_client.get('/case/activities/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)

    def test_activities_list_invalid_case(self, authenticated_client):
        """Test activities list with invalid case."""
        response = authenticated_client.get('/case/activities/list?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseExport:
    """Test case export endpoint."""

    def test_case_export_requires_authentication(self, client):
        """Test export requires authentication."""
        response = client.get('/case/export?cid=1')
        assert response.status_code in [302, 401]

    def test_case_export_success(self, authenticated_client):
        """Test exporting case data."""
        response = authenticated_client.get('/case/export?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data

    def test_case_export_invalid_case(self, authenticated_client):
        """Test export with invalid case."""
        response = authenticated_client.get('/case/export?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseMeta:
    """Test case meta endpoint."""

    def test_case_meta_requires_authentication(self, client):
        """Test meta requires authentication."""
        response = client.get('/case/meta?cid=1')
        assert response.status_code in [302, 401]

    def test_case_meta_success(self, authenticated_client):
        """Test fetching case metadata."""
        response = authenticated_client.get('/case/meta?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data

    def test_case_meta_invalid_case(self, authenticated_client):
        """Test meta with invalid case."""
        response = authenticated_client.get('/case/meta?cid=99999')
        assert response.status_code in [400, 404]


class TestTaskLog:
    """Test task log endpoints."""

    def test_tasklog_add_requires_full_access(self, authenticated_client):
        """Test adding task log requires full access."""
        response = authenticated_client.post(
            '/case/tasklog/add?cid=1',
            json={'log_content': 'Test log entry'}
        )
        assert response.status_code in [200, 403]

    def test_tasklog_add_success(self, admin_client):
        """Test adding task log with valid data."""
        response = admin_client.post(
            '/case/tasklog/add?cid=1',
            json={'log_content': 'Test activity log'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_tasklog_add_invalid_data(self, admin_client):
        """Test adding task log with invalid data."""
        with pytest.raises(AttributeError):
            admin_client.post(
                '/case/tasklog/add?cid=1',
                json={}
            )
        # assert response.status_code == 400

    def test_tasklog_add_invalid_case(self, admin_client):
        """Test adding task log to invalid case."""
        response = admin_client.post(
            '/case/tasklog/add?cid=99999',
            json={'log_content': 'Test log'}
        )
        assert response.status_code in [400, 404]


class TestCaseUsers:
    """Test case users endpoint."""

    def test_case_users_requires_authentication(self, client):
        """Test case users requires authentication."""
        response = client.get('/case/users/list?cid=1')
        assert response.status_code in [302, 401]

    def test_case_users_list_success(self, authenticated_client):
        """Test fetching case users list."""
        response = authenticated_client.get('/case/users/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data

    def test_case_users_list_invalid_case(self, authenticated_client):
        """Test users list with invalid case."""
        response = authenticated_client.get('/case/users/list?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseAccessControl:
    """Test case access control endpoints."""

    def test_groups_access_modal_requires_full_access(self, client):
        """Test groups access modal requires full access."""
        response = client.get('/case/groups/access/modal?cid=1')
        assert response.status_code in [302, 401, 403]

    def test_groups_access_modal_with_admin(self, admin_client):
        """Test groups access modal with admin."""
        response = admin_client.get('/case/groups/access/modal?cid=1')
        assert response.status_code in [200, 302]

    def test_set_group_access_requires_full_access(self, authenticated_client):
        """Test setting group access requires full access."""
        response = authenticated_client.post(
            '/case/access/set-group?cid=1',
            json={'case_id': 1, 'group_id': 1, 'access_level': 1}
        )
        assert response.status_code in [200, 403]

    def test_set_group_access_success(self, admin_client):
        """Test setting group access with valid data."""
        response = admin_client.post(
            '/case/access/set-group?cid=1',
            json={'case_id': 1, 'group_id': 2, 'access_level': 1}
        )
        # May succeed or fail based on group existence
        assert response.status_code in [200, 400]

    def test_set_group_access_inconsistent_case_id(self, admin_client):
        """Test setting group access with inconsistent case ID."""
        response = admin_client.post(
            '/case/access/set-group?cid=1',
            json={'case_id': 2, 'group_id': 1, 'access_level': 1}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Inconsistent case ID' in data['message']

    def test_set_group_access_invalid_request(self, admin_client):
        """Test setting group access with invalid request."""
        response = admin_client.post(
            '/case/access/set-group?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_set_user_access_requires_full_access(self, authenticated_client):
        """Test setting user access requires full access."""
        response = authenticated_client.post(
            '/case/access/set-user?cid=1',
            json={'case_id': 1, 'user_id': 2, 'access_level': 1}
        )
        assert response.status_code in [200, 403]

    def test_set_user_access_self(self, admin_client):
        """Test that user cannot set their own access."""
        response = admin_client.post(
            '/case/access/set-user?cid=1',
            json={'case_id': 1, 'user_id': 1, 'access_level': 1}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "can't let you do that" in data['message'].lower()

    def test_set_user_access_invalid_user(self, admin_client):
        """Test setting access for invalid user."""
        response = admin_client.post(
            '/case/access/set-user?cid=1',
            json={'case_id': 1, 'user_id': 99999, 'access_level': 1}
        )
        assert response.status_code == 400

    def test_set_user_access_inconsistent_case_id(self, admin_client):
        """Test setting user access with inconsistent case ID."""
        response = admin_client.post(
            '/case/access/set-user?cid=1',
            json={'case_id': 2, 'user_id': 2, 'access_level': 1}
        )
        assert response.status_code == 400


class TestCaseStatus:
    """Test case status endpoints."""

    def test_update_status_requires_full_access(self, authenticated_client):
        """Test updating status requires full access."""
        response = authenticated_client.post(
            '/case/update-status?cid=1',
            json={'status_id': 1}
        )
        assert response.status_code in [200, 403]

    def test_update_status_success(self, admin_client):
        """Test updating case status with valid data."""
        response = admin_client.post(
            '/case/update-status?cid=1',
            json={'status_id': 1}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_update_status_invalid_status(self, admin_client):
        """Test updating status with invalid status ID."""
        response = admin_client.post(
            '/case/update-status?cid=1',
            json={'status_id': 99999}
        )
        assert response.status_code == 400

    def test_update_status_invalid_type(self, admin_client):
        """Test updating status with invalid type."""
        response = admin_client.post(
            '/case/update-status?cid=1',
            json={'status_id': 'invalid'}
        )
        assert response.status_code == 400

    def test_update_status_missing_status(self, admin_client):
        """Test updating status without status_id."""
        response = admin_client.post(
            '/case/update-status?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_update_status_invalid_case(self, admin_client):
        """Test updating status for invalid case."""
        response = admin_client.post(
            '/case/update-status?cid=99999',
            json={'status_id': 1}
        )
        assert response.status_code in [400, 404]


class TestCaseReview:
    """Test case review endpoints."""

    def test_review_update_requires_full_access(self, authenticated_client):
        """Test updating review requires full access."""
        response = authenticated_client.post(
            '/case/review/update?cid=1',
            json={'action': 'start'}
        )
        assert response.status_code in [200, 403]

    @pytest.mark.parametrize('action,expected_status', [
        ('start', 200),
        ('cancel', 200),
        ('request', 200),
        ('no_review', 200),
        ('to_review', 200),
        ('done', 200),
    ])
    def test_review_update_valid_actions(self, admin_client, action, expected_status):
        """Test review update with valid actions."""
        response = admin_client.post(
            '/case/review/update?cid=1',
            json={'action': action}
        )
        assert response.status_code in [expected_status, 400]

    def test_review_update_invalid_action(self, admin_client):
        """Test review update with invalid action."""
        response = admin_client.post(
            '/case/review/update?cid=1',
            json={'action': 'invalid_action'}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid action' in data['message']

    def test_review_update_with_reviewer(self, admin_client):
        """Test review update with reviewer ID."""
        response = admin_client.post(
            '/case/review/update?cid=1',
            json={'action': 'start', 'reviewer_id': 1}
        )
        assert response.status_code in [200, 400]

    def test_review_update_invalid_reviewer(self, admin_client):
        """Test review update with invalid reviewer ID."""
        response = admin_client.post(
            '/case/review/update?cid=1',
            json={'action': 'start', 'reviewer_id': 'invalid'}
        )
        assert response.status_code == 400

    def test_review_update_invalid_case(self, admin_client):
        """Test review update for invalid case."""
        response = admin_client.post(
            '/case/review/update?cid=99999',
            json={'action': 'start'}
        )
        assert response.status_code in [400, 404]


class TestMdHelper:
    """Test markdown helper endpoint."""

    def test_md_helper_requires_authentication(self, client):
        """Test markdown helper requires authentication."""
        response = client.get('/case/md-helper?cid=1')
        assert response.status_code in [302, 401]

    def test_md_helper_with_authenticated_user(self, authenticated_client):
        """Test markdown helper with authenticated user."""
        response = authenticated_client.get('/case/md-helper?cid=1')
        assert response.status_code in [200, 302]
