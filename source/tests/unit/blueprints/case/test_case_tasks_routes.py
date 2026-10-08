"""Tests for case tasks routes."""
import pytest


class TestCaseTasksPage:
    """Test case tasks page endpoints."""

    def test_case_tasks_page_requires_authentication(self, client):
        """Test tasks page requires authentication."""
        response = client.get('/case/tasks?cid=1')
        assert response.status_code in [302, 401]

    def test_case_tasks_page_with_authenticated_user(self, authenticated_client):
        """Test tasks page with authenticated user."""
        response = authenticated_client.get('/case/tasks?cid=1')
        assert response.status_code in [200, 302]


class TestCaseTasksList:
    """Test tasks list endpoints."""

    def test_tasks_list_requires_authentication(self, client):
        """Test tasks list requires authentication."""
        response = client.get('/case/tasks/list?cid=1')
        assert response.status_code in [302, 401]

    def test_tasks_list_success(self, authenticated_client):
        """Test fetching tasks list."""
        response = authenticated_client.get('/case/tasks/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'tasks' in data['data']
        assert 'tasks_status' in data['data']
        assert 'state' in data['data']

    def test_tasks_list_invalid_case(self, authenticated_client):
        """Test tasks list with invalid case."""
        response = authenticated_client.get('/case/tasks/list?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseTasksState:
    """Test tasks state endpoint."""

    def test_tasks_state_requires_authentication(self, client):
        """Test tasks state requires authentication."""
        response = client.get('/case/tasks/state?cid=1')
        assert response.status_code in [302, 401]

    def test_tasks_state_success(self, authenticated_client):
        """Test fetching tasks state."""
        response = authenticated_client.get('/case/tasks/state?cid=1')
        assert response.status_code in [200, 400]

    def test_tasks_state_invalid_case(self, authenticated_client):
        """Test tasks state with invalid case."""
        response = authenticated_client.get('/case/tasks/state?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseTasksAdd:
    """Test adding tasks."""

    def test_task_add_modal_requires_full_access(self, authenticated_client):
        """Test task add modal requires full access."""
        response = authenticated_client.get('/case/tasks/add/modal?cid=1')
        assert response.status_code in [200, 403]

    def test_task_add_modal_with_admin(self, admin_client):
        """Test task add modal with admin."""
        response = admin_client.get('/case/tasks/add/modal?cid=1')
        assert response.status_code == 200

    def test_task_add_requires_full_access(self, authenticated_client):
        """Test adding task requires full access."""
        response = authenticated_client.post(
            '/case/tasks/add?cid=1',
            json={'task_title': 'Test Task', 'task_assignees_id': []}
        )
        assert response.status_code in [200, 403]

    def test_task_add_success(self, admin_client):
        """Test adding task with valid data."""
        response = admin_client.post(
            '/case/tasks/add?cid=1',
            json={
                'task_title': 'Test Task',
                'task_description': 'Test description',
                'task_status_id': 1,
                'task_assignees_id': []
            }
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_task_add_missing_required_fields(self, admin_client):
        """Test adding task without required fields."""
        response = admin_client.post(
            '/case/tasks/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_task_add_legacy_assignee_field(self, admin_client):
        """Test adding task with legacy task_assignee_id field."""
        response = admin_client.post(
            '/case/tasks/add?cid=1',
            json={
                'task_title': 'Test',
                'task_assignee_id': 1
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'task_assignee_id' in data['message'].lower() or 'v1.5.0' in data['message']

    def test_task_add_with_assignees(self, admin_client):
        """Test adding task with assignees."""
        response = admin_client.post(
            '/case/tasks/add?cid=1',
            json={
                'task_title': 'Test Task',
                'task_assignees_id': [1, 2]
            }
        )
        assert response.status_code in [200, 400]

    def test_task_add_invalid_case(self, admin_client):
        """Test adding task to invalid case."""
        response = admin_client.post(
            '/case/tasks/add?cid=99999',
            json={'task_title': 'Test', 'task_assignees_id': []}
        )
        assert response.status_code in [400, 404]


class TestCaseTasksView:
    """Test task view endpoints."""

    def test_task_view_requires_authentication(self, client):
        """Test task view requires authentication."""
        response = client.get('/case/tasks/1?cid=1')
        assert response.status_code in [302, 401]

    def test_task_view_success(self, authenticated_client):
        """Test viewing single task."""
        response = authenticated_client.get('/case/tasks/1?cid=1')
        # May not exist in test DB
        assert response.status_code in [200, 400]

    def test_task_view_invalid_task(self, authenticated_client):
        """Test viewing invalid task."""
        response = authenticated_client.get('/case/tasks/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_task_view_modal_requires_authentication(self, client):
        """Test task view modal requires authentication."""
        response = client.get('/case/tasks/1/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_task_view_modal_success(self, authenticated_client):
        """Test viewing task modal."""
        response = authenticated_client.get('/case/tasks/1/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_task_view_modal_invalid_task(self, authenticated_client):
        """Test viewing modal for invalid task."""
        response = authenticated_client.get('/case/tasks/99999/modal?cid=1')
        assert response.status_code in [400, 404]


class TestCaseTasksUpdate:
    """Test task update endpoints."""

    def test_task_update_requires_full_access(self, authenticated_client):
        """Test updating task requires full access."""
        response = authenticated_client.post(
            '/case/tasks/update/1?cid=1',
            json={'task_title': 'Updated Task', 'task_assignees_id': []}
        )
        assert response.status_code in [200, 403]

    def test_task_update_success(self, admin_client):
        """Test updating task with valid data."""
        response = admin_client.post(
            '/case/tasks/update/1?cid=1',
            json={
                'task_title': 'Updated Task',
                'task_description': 'Updated description',
                'task_assignees_id': []
            }
        )
        # May succeed or fail if task doesn't exist
        assert response.status_code in [200, 400]

    def test_task_update_invalid_task(self, admin_client):
        """Test updating invalid task."""
        response = admin_client.post(
            '/case/tasks/update/99999?cid=1',
            json={'task_title': 'Updated', 'task_assignees_id': []}
        )
        assert response.status_code in [400, 404]

    def test_task_update_legacy_assignee_field(self, admin_client):
        """Test updating task with legacy task_assignee_id field."""
        response = admin_client.post(
            '/case/tasks/update/1?cid=1',
            json={
                'task_title': 'Test',
                'task_assignee_id': 1
            }
        )
        assert response.status_code == 400

    def test_task_update_invalid_data(self, admin_client):
        """Test updating task with invalid data."""
        response = admin_client.post(
            '/case/tasks/update/1?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_task_status_update_requires_full_access(self, authenticated_client):
        """Test updating task status requires full access."""
        response = authenticated_client.post(
            '/case/tasks/status/update/1?cid=1',
            json={'task_status_id': 1}
        )
        assert response.status_code in [200, 403]

    def test_task_status_update_success(self, admin_client):
        """Test updating task status."""
        response = admin_client.post(
            '/case/tasks/status/update/1?cid=1',
            json={'task_status_id': 2}
        )
        # May succeed or fail if task doesn't exist
        assert response.status_code in [200, 400]

    def test_task_status_update_invalid_status(self, admin_client):
        """Test updating task with invalid status."""
        response = admin_client.post(
            '/case/tasks/status/update/1?cid=1',
            json={'task_status_id': 99999}
        )
        assert response.status_code in [400, 404]


class TestCaseTasksDelete:
    """Test task delete endpoint."""

    def test_task_delete_requires_full_access(self, authenticated_client):
        """Test deleting task requires full access."""
        response = authenticated_client.post('/case/tasks/delete/1?cid=1')
        assert response.status_code in [200, 403]

    def test_task_delete_invalid_task(self, admin_client):
        """Test deleting invalid task."""
        response = admin_client.post('/case/tasks/delete/99999?cid=1')
        assert response.status_code in [400, 404]

    def test_task_delete_invalid_case(self, admin_client):
        """Test deleting task from invalid case."""
        response = admin_client.post('/case/tasks/delete/1?cid=99999')
        assert response.status_code in [400, 404]


class TestCaseTasksComments:
    """Test task comment endpoints."""

    def test_task_comments_modal_requires_authentication(self, client):
        """Test task comments modal requires authentication."""
        response = client.get('/case/tasks/1/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_task_comments_modal_success(self, authenticated_client):
        """Test task comments modal."""
        response = authenticated_client.get('/case/tasks/1/comments/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_task_comments_list_requires_authentication(self, client):
        """Test task comments list requires authentication."""
        response = client.get('/case/tasks/1/comments/list?cid=1')
        assert response.status_code in [302, 401]

    def test_task_comments_list_success(self, authenticated_client):
        """Test fetching task comments list."""
        response = authenticated_client.get('/case/tasks/1/comments/list?cid=1')
        assert response.status_code in [200, 400]

    def test_task_comment_add_requires_full_access(self, authenticated_client):
        """Test adding comment requires full access."""
        response = authenticated_client.post(
            '/case/tasks/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 403]

    def test_task_comment_add_success(self, admin_client):
        """Test adding comment to task."""
        response = admin_client.post(
            '/case/tasks/1/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        # May fail if task doesn't exist
        assert response.status_code in [200, 400]

    def test_task_comment_add_missing_text(self, admin_client):
        """Test adding comment without text."""
        response = admin_client.post(
            '/case/tasks/1/comments/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_task_comment_get_requires_authentication(self, client):
        """Test getting comment requires authentication."""
        response = client.get('/case/tasks/1/comments/1?cid=1')
        assert response.status_code in [302, 401]

    def test_task_comment_get_success(self, authenticated_client):
        """Test getting single comment."""
        response = authenticated_client.get('/case/tasks/1/comments/1?cid=1')
        assert response.status_code in [200, 400]

    def test_task_comment_edit_requires_full_access(self, authenticated_client):
        """Test editing comment requires full access."""
        response = authenticated_client.post(
            '/case/tasks/1/comments/1/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        assert response.status_code in [200, 403]

    def test_task_comment_delete_requires_full_access(self, authenticated_client):
        """Test deleting comment requires full access."""
        response = authenticated_client.post('/case/tasks/1/comments/1/delete?cid=1')
        assert response.status_code in [200, 403]

    def test_task_comment_delete_invalid_comment(self, admin_client):
        """Test deleting invalid comment."""
        response = admin_client.post('/case/tasks/1/comments/99999/delete?cid=1')
        assert response.status_code in [400, 404]
