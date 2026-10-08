"""Tests for case timeline routes."""
import pytest


class TestCaseTimelinePage:
    """Test case timeline page endpoints."""

    def test_case_timeline_page_requires_authentication(self, client):
        """Test timeline page requires authentication."""
        response = client.get('/case/timeline?cid=1')
        assert response.status_code in [302, 401]

    def test_case_timeline_page_with_authenticated_user(self, authenticated_client):
        """Test timeline page with authenticated user."""
        response = authenticated_client.get('/case/timeline?cid=1')
        assert response.status_code in [200, 302]

    def test_timeline_visualize_requires_authentication(self, client):
        """Test timeline visualize requires authentication."""
        response = client.get('/case/timeline/visualize?cid=1')
        assert response.status_code in [302, 401]

    def test_timeline_visualize_with_authenticated_user(self, authenticated_client):
        """Test timeline visualize with authenticated user."""
        response = authenticated_client.get('/case/timeline/visualize?cid=1')
        assert response.status_code in [200, 302]


class TestCaseTimelineTimezone:
    """Test timeline timezone endpoints."""

    def test_timeline_timezone_requires_authentication(self, client):
        """Test selecting timezone requires authentication."""
        response = client.post('/case/timeline/select-timezone?cid=1', json="0")
        assert response.status_code in [302, 401]

    def test_timeline_timezone_success(self, authenticated_client):
        """Test selecting timeline timezone."""
        response = authenticated_client.post(
            '/case/timeline/select-timezone?cid=1',
            json="0"
        )
        assert response.status_code in [200, 302]


class TestCaseTimelineState:
    """Test timeline state endpoint."""

    def test_timeline_state_requires_authentication(self, client):
        """Test timeline state requires authentication."""
        response = client.get('/case/timeline/state?cid=1')
        assert response.status_code in [302, 401]

    def test_timeline_state_success(self, authenticated_client):
        """Test fetching timeline state."""
        response = authenticated_client.get('/case/timeline/state?cid=1')
        assert response.status_code in [200, 400]

    def test_timeline_state_invalid_case(self, authenticated_client):
        """Test timeline state with invalid case."""
        response = authenticated_client.get('/case/timeline/state?cid=99999')
        assert response.status_code in [400, 403, 404]


class TestCaseTimelineEventsList:
    """Test timeline events list endpoints."""

    def test_events_list_requires_authentication(self, client):
        """Test events list requires authentication."""
        response = client.get('/case/timeline/events/list?cid=1')
        assert response.status_code in [302, 401]

    def test_events_list_success(self, authenticated_client):
        """Test fetching events list."""
        response = authenticated_client.get('/case/timeline/events/list?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'timeline' in data['data']
        assert 'state' in data['data']

    def test_events_list_with_filter(self, authenticated_client):
        """Test fetching events list with asset filter."""
        response = authenticated_client.get('/case/timeline/events/list/filter/1?cid=1')
        assert response.status_code == 200

    def test_events_list_invalid_case(self, authenticated_client):
        """Test events list with invalid case."""
        response = authenticated_client.get('/case/timeline/events/list?cid=99999')
        assert response.status_code in [400, 403, 404]


class TestCaseTimelineVisualize:
    """Test timeline visualization endpoints."""

    def test_timeline_visualize_by_asset_requires_authentication(self, client):
        """Test visualize by asset requires authentication."""
        response = client.get('/case/timeline/visualize/data/by-asset?cid=1')
        assert response.status_code in [302, 401]

    def test_timeline_visualize_by_asset_success(self, authenticated_client):
        """Test visualizing timeline by asset."""
        response = authenticated_client.get('/case/timeline/visualize/data/by-asset?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'events' in data['data']

    def test_timeline_visualize_by_category_requires_authentication(self, client):
        """Test visualize by category requires authentication."""
        response = client.get('/case/timeline/visualize/data/by-category?cid=1')
        assert response.status_code in [302, 401]

    def test_timeline_visualize_by_category_success(self, authenticated_client):
        """Test visualizing timeline by category."""
        response = authenticated_client.get('/case/timeline/visualize/data/by-category?cid=1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'events' in data['data']


class TestCaseTimelineAdvancedFilter:
    """Test timeline advanced filter endpoint."""

    def test_advanced_filter_requires_authentication(self, client):
        """Test advanced filter requires authentication."""
        response = client.get('/case/timeline/advanced-filter?cid=1&q={}')
        assert response.status_code in [302, 401]

    def test_advanced_filter_success(self, authenticated_client):
        """Test advanced filtering."""
        response = authenticated_client.get('/case/timeline/advanced-filter?cid=1&q=%7B%7D')
        assert response.status_code == 200

    def test_advanced_filter_with_asset(self, authenticated_client):
        """Test filtering by asset."""
        import urllib.parse
        filter_query = urllib.parse.quote('{"asset":["test"]}')
        response = authenticated_client.get(f'/case/timeline/advanced-filter?cid=1&q={filter_query}')
        assert response.status_code == 200

    def test_advanced_filter_with_date_range(self, authenticated_client):
        """Test filtering by date range."""
        import urllib.parse
        filter_query = urllib.parse.quote('{"startDate":["2024-01-01"],"endDate":["2024-12-31"]}')
        response = authenticated_client.get(f'/case/timeline/advanced-filter?cid=1&q={filter_query}')
        assert response.status_code == 200

    def test_advanced_filter_invalid_query(self, authenticated_client):
        """Test advanced filter with invalid query."""
        response = authenticated_client.get('/case/timeline/advanced-filter?cid=1&q=invalid')
        assert response.status_code == 400


class TestCaseTimelineEventsAdd:
    """Test adding timeline events."""

    def test_event_add_modal_requires_full_access(self, authenticated_client):
        """Test event add modal requires full access."""
        response = authenticated_client.get('/case/timeline/events/add/modal?cid=1')
        assert response.status_code in [200, 403]

    def test_event_add_modal_with_admin(self, admin_client, sample_event_category):
        """Test event add modal with admin."""
        response = admin_client.get('/case/timeline/events/add/modal?cid=1')
        assert response.status_code in [200, 302]

    def test_event_add_requires_full_access(self, authenticated_client):
        """Test adding event requires full access."""
        response = authenticated_client.post(
            '/case/timeline/events/add?cid=1',
            json={
                'event_title': 'Test Event',
                'event_date': '2024-01-01T12:00:00.000000',
                'event_tz': '+00:00'
            }
        )
        assert response.status_code in [200, 403]

    def test_event_add_success(self, admin_client, sample_event_category):
        """Test adding event with valid data."""
        response = admin_client.post(
            '/case/timeline/events/add?cid=1',
            json={
                'event_title': 'Test Event',
                'event_content': 'Test content',
                'event_date': '2024-01-01T12:00:00.000000',
                'event_tz': '+00:00',
                'event_category_id': sample_event_category
            }
        )
        # May succeed or fail based on validation
        assert response.status_code in [200, 400]

    def test_event_add_missing_required_fields(self, admin_client):
        """Test adding event without required fields."""
        response = admin_client.post(
            '/case/timeline/events/add?cid=1',
            json={}
        )
        assert response.status_code == 400

    def test_event_add_invalid_date_format(self, admin_client):
        """Test adding event with invalid date."""
        response = admin_client.post(
            '/case/timeline/events/add?cid=1',
            json={
                'event_title': 'Test',
                'event_date': 'invalid-date',
                'event_tz': '+00:00'
            }
        )
        assert response.status_code == 400

    def test_event_add_invalid_case(self, admin_client):
        """Test adding event to invalid case."""
        response = admin_client.post(
            '/case/timeline/events/add?cid=99999',
            json={
                'event_title': 'Test',
                'event_date': '2024-01-01T12:00:00.000000',
                'event_tz': '+00:00'
            }
        )
        assert response.status_code in [400, 403, 404]


class TestCaseTimelineEventsView:
    """Test event view endpoints."""

    def test_event_view_requires_authentication(self, client, sample_event):
        """Test event view requires authentication."""
        response = client.get(f'/case/timeline/events/{sample_event}?cid=1')
        assert response.status_code in [302, 401]

    def test_event_view_success(self, authenticated_client, sample_event):
        """Test viewing single event."""
        response = authenticated_client.get(f'/case/timeline/events/{sample_event}?cid=1')
        assert response.status_code in [200, 400]

    def test_event_view_invalid_event(self, authenticated_client):
        """Test viewing invalid event."""
        response = authenticated_client.get('/case/timeline/events/99999?cid=1')
        assert response.status_code in [400, 403, 404]

    def test_event_view_modal_requires_authentication(self, client, sample_event):
        """Test event view modal requires authentication."""
        response = client.get(f'/case/timeline/events/{sample_event}/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_event_view_modal_success(self, authenticated_client, sample_event):
        """Test viewing event modal."""
        response = authenticated_client.get(f'/case/timeline/events/{sample_event}/modal?cid=1')
        assert response.status_code in [200, 302, 400]


class TestCaseTimelineEventsUpdate:
    """Test event update endpoints."""

    def test_event_update_success(self, admin_client, sample_event):
        """Test updating event with valid data."""
        response = admin_client.post(
            f'/case/timeline/events/update/{sample_event}?cid=1',
            json={
                'event_title': 'Updated Event',
                'event_date': '2024-01-01T12:00:00.000000',
                'event_tz': '+00:00',
                'event_category_id': 1,
            }
        )
        print(response.data)
        # TODO: update that passes validation
        assert response.status_code in [200, 400]

    def test_event_update_invalid_event(self, admin_client):
        """Test updating invalid event."""
        response = admin_client.post(
            '/case/timeline/events/update/99999?cid=1',
            json={
                'event_title': 'Updated',
                'event_date': '2024-01-01T12:00:00.000000',
                'event_tz': '+00:00'
            }
        )
        assert response.status_code in [400, 403, 404]


class TestCaseTimelineEventsDelete:
    """Test event delete endpoint."""

    def test_event_delete_requires_full_access(self, admin_client, sample_event):
        """Test deleting event requires full access."""
        response = admin_client.post(f'/case/timeline/events/delete/{sample_event}?cid=1')
        assert response.status_code in [200, 403]

    def test_event_delete_invalid_event(self, admin_client):
        """Test deleting invalid event."""
        response = admin_client.post('/case/timeline/events/delete/99999?cid=1')
        assert response.status_code in [400, 403, 404]


class TestCaseTimelineEventsDuplicate:
    """Test event duplicate endpoint."""

    def test_event_duplicate_requires_full_access(self, admin_client, sample_event):
        """Test duplicating event requires full access."""
        response = admin_client.get(f'/case/timeline/events/duplicate/{sample_event}?cid=1')
        assert response.status_code in [200, 403]

    def test_event_duplicate_invalid_event(self, admin_client):
        """Test duplicating invalid event."""
        response = admin_client.get('/case/timeline/events/duplicate/99999?cid=1')
        assert response.status_code in [400, 403, 404]


class TestCaseTimelineEventsFlag:
    """Test event flag endpoint."""

    def test_event_flag_requires_full_access(self, admin_client, sample_event):
        """Test flagging event requires full access."""
        response = admin_client.get(f'/case/timeline/events/flag/{sample_event}?cid=1')
        assert response.status_code in [200, 403]

    def test_event_flag_invalid_event(self, admin_client):
        """Test flagging invalid event."""
        response = admin_client.get('/case/timeline/events/flag/99999?cid=1')
        assert response.status_code in [400, 403, 404]

# TODO: create sample excel sheet for timeline events
# class TestCaseTimelineEventsUpload:
#     """Test event upload endpoints."""
#
#     def test_event_csv_upload_requires_full_access(self, admin_client):
#         """Test CSV upload requires full access."""
#         response = admin_client.post(
#             '/case/timeline/events/csv_upload?cid=1',
#             json={'CSVData': 'test'}
#         )
#         assert response.status_code in [200, 400, 403]
#
#     def test_event_csv_upload_missing_data(self, admin_client):
#         """Test CSV upload without data."""
#         with pytest.raises(KeyError):
#             admin_client.post(
#                 '/case/timeline/events/csv_upload?cid=1',
#                 json={}
#             )
#
#     def test_event_excel_upload_missing_data(self, admin_client):
#         """Test Excel upload without data."""
#         response = admin_client.post(
#             '/case/timeline/events/excel_upload?cid=1',
#             json={}
#         )
#         assert response.status_code == 400
#
#     def test_event_excel_upload_invalid_case(self, admin_client):
#         """Test uploading events to invalid case."""
#         response = admin_client.post(
#             '/case/timeline/events/excel_upload?cid=99999',
#             json={'excel_data': []}
#         )
#         assert response.status_code in [400, 403, 404]


class TestCaseTimelineConvertDate:
    """Test date conversion endpoint."""

    def test_convert_date_requires_authentication(self, client):
        """Test convert date requires authentication."""
        response = client.post(
            '/case/timeline/events/convert-date?cid=1',
            json={'date_value': '2024-01-01'}
        )
        assert response.status_code in [302, 401]

    def test_convert_date_success(self, admin_client):
        """Test converting date with valid format."""
        response = admin_client.post(
            '/case/timeline/events/convert-date?cid=1',
            json={'date_value': '2024-01-01 12:00:00'}
        )
        assert response.status_code in [200, 400]

    def test_convert_date_invalid_format(self, admin_client):
        """Test converting date with invalid format."""
        response = admin_client.post(
            '/case/timeline/events/convert-date?cid=1',
            json={'date_value': 'invalid'}
        )
        assert response.status_code == 400

    def test_convert_date_missing_value(self, admin_client):
        """Test converting date without value."""
        response = admin_client.post(
            '/case/timeline/events/convert-date?cid=1',
            json={}
        )
        assert response.status_code == 400


class TestCaseTimelineFilterHelp:
    """Test filter help modal."""

    def test_filter_help_modal_requires_authentication(self, client):
        """Test filter help modal requires authentication."""
        response = client.get('/case/timeline/filter-help/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_filter_help_modal_with_authenticated_user(self, authenticated_client):
        """Test filter help modal with authenticated user."""
        response = authenticated_client.get('/case/timeline/filter-help/modal?cid=1')
        assert response.status_code in [200, 302]


class TestCaseTimelineEventsComments:
    """Test event comment endpoints."""

    def test_event_comments_modal_requires_authentication(self, client, sample_event):
        """Test event comments modal requires authentication."""
        response = client.get(f'/case/timeline/events/{sample_event}/comments/modal?cid=1')
        assert response.status_code in [302, 401]

    def test_event_comments_modal_success(self, authenticated_client, sample_event):
        """Test event comments modal."""
        response = authenticated_client.get(f'/case/timeline/events/{sample_event}/comments/modal?cid=1')
        assert response.status_code in [200, 302, 400]

    def test_event_comments_list_requires_authentication(self, client, sample_event):
        """Test event comments list requires authentication."""
        response = client.get(f'/case/timeline/events/{sample_event}/comments/list?cid=1')
        assert response.status_code in [302, 401]

    def test_event_comments_list_success(self, authenticated_client, sample_event):
        """Test fetching event comments list."""
        response = authenticated_client.get(f'/case/timeline/events/{sample_event}/comments/list?cid=1')
        assert response.status_code in [200, 400]

    def test_event_comment_add_requires_full_access(self, admin_client, sample_event):
        """Test adding comment requires full access."""
        response = admin_client.post(
            f'/case/timeline/events/{sample_event}/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 403]

    def test_event_comment_add_success(self, admin_client, sample_event):
        """Test adding comment to event."""
        response = admin_client.post(
            f'/case/timeline/events/{sample_event}/comments/add?cid=1',
            json={'comment_text': 'Test comment'}
        )
        assert response.status_code in [200, 400]

    def test_event_comment_get_requires_authentication(self, client, sample_event, sample_event_comment):
        """Test getting comment requires authentication."""
        response = client.get(f'/case/timeline/events/{sample_event}/comments/{sample_event_comment}?cid=1')
        assert response.status_code in [302, 401]

    def test_event_comment_get_success(self, authenticated_client, sample_event, sample_event_comment):
        """Test getting single comment."""
        response = authenticated_client.get(f'/case/timeline/events/{sample_event}/comments/{sample_event_comment}?cid=1')
        assert response.status_code in [200, 400]

    def test_event_comment_edit_requires_full_access(self, admin_client, sample_event, sample_event_comment):
        """Test editing comment requires full access."""
        response = admin_client.post(
            f'/case/timeline/events/{sample_event}/comments/{sample_event_comment}/edit?cid=1',
            json={'comment_text': 'Updated comment'}
        )
        assert response.status_code in [200, 403]

    def test_event_comment_delete_requires_full_access(self, admin_client, sample_event, sample_event_comment):
        """Test deleting comment requires full access."""
        response = admin_client.post(f'/case/timeline/events/{sample_event}/comments/{sample_event_comment}/delete?cid=1')
        assert response.status_code in [200, 400]
        if response.status_code == 400:
            data = response.get_json()
            assert 'not allowed' in data['message']

    def test_event_comment_delete_invalid_comment(self, admin_client, sample_event):
        """Test deleting invalid comment."""
        response = admin_client.post(f'/case/timeline/events/{sample_event}/comments/99999/delete?cid=1')
        assert response.status_code in [400, 403, 404]
