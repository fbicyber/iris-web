# Case Blueprint Test Coverage

This directory contains comprehensive tests for all route files in the case blueprint.

## Test Files Generated

### 1. test_case_routes.py (422 lines)
Tests for main case routes (`case_routes.py`):
- **TestCaseRoutes**: Main case page access and pipelines modal
- **TestCaseSummary**: Case summary update and fetch endpoints
- **TestCaseActivities**: Activity list and tracking
- **TestCaseExport**: Case export functionality
- **TestCaseMeta**: Case metadata retrieval
- **TestTaskLog**: Task log addition
- **TestCaseUsers**: Case users list
- **TestCaseAccessControl**: Group and user access control (set-group, set-user)
- **TestCaseStatus**: Case status updates
- **TestCaseReview**: Case review workflow (start, cancel, request, done, etc.)
- **TestMdHelper**: Markdown helper endpoint

**Key Coverage:**
- Authentication and authorization for all endpoints
- Access control decorators (`@ac_case_requires`, `@ac_api_case_requires`)
- Full access requirements for state-changing operations
- Invalid case ID handling
- Review workflow with multiple actions
- Access control for groups and users

### 2. test_case_ioc_routes.py (405 lines)
Tests for IOC routes (`case_ioc_routes.py`):
- **TestCaseIocPage**: IOC page rendering
- **TestCaseIocList**: IOC listing with state
- **TestCaseIocState**: IOC state management
- **TestCaseIocAdd**: Adding IOCs with validation
- **TestCaseIocUpload**: CSV upload with headers and validation
- **TestCaseIocModal**: Add and view modals
- **TestCaseIocView**: Single IOC viewing
- **TestCaseIocUpdate**: IOC updates
- **TestCaseIocDelete**: IOC deletion
- **TestCaseIocComments**: Complete comment CRUD operations

**Key Coverage:**
- IOC CRUD operations
- CSV upload with header detection
- IOC type and TLP validation
- Comment lifecycle for IOCs
- State tracking

### 3. test_case_assets_routes.py (377 lines)
Tests for asset routes (`case_assets_routes.py`):
- **TestCaseAssetsPage**: Assets page rendering
- **TestCaseAssetsList**: Asset filtering and listing
- **TestCaseAssetsState**: Asset state management
- **TestCaseAssetsAdd**: Adding assets with validation
- **TestCaseAssetsUpload**: CSV upload functionality
- **TestCaseAssetsView**: Single asset viewing with modals
- **TestCaseAssetsUpdate**: Asset updates
- **TestCaseAssetsDelete**: Asset deletion
- **TestCaseAssetsComments**: Complete comment CRUD operations

**Key Coverage:**
- Asset CRUD operations
- CSV upload with type validation
- Asset type, analysis status, compromise status
- Duplicate asset detection
- IOC linking to assets
- Comment lifecycle for assets

### 4. test_case_tasks_routes.py (343 lines)
Tests for task routes (`case_tasks_routes.py`):
- **TestCaseTasksPage**: Tasks page rendering
- **TestCaseTasksList**: Task listing with status
- **TestCaseTasksState**: Task state management
- **TestCaseTasksAdd**: Adding tasks with assignees
- **TestCaseTasksView**: Single task viewing with modals
- **TestCaseTasksUpdate**: Task updates and status changes
- **TestCaseTasksDelete**: Task deletion
- **TestCaseTasksComments**: Complete comment CRUD operations

**Key Coverage:**
- Task CRUD operations
- Multiple assignees support (task_assignees_id array)
- Legacy field rejection (task_assignee_id)
- Task status updates
- Comment lifecycle for tasks

### 5. test_case_notes_routes.py (390 lines)
Tests for notes routes (`case_notes_routes.py`):
- **TestCaseNotesPage**: Notes page rendering
- **TestCaseNotesState**: Notes state management
- **TestCaseNotesDetail**: Single note viewing with comments
- **TestCaseNotesAdd**: Adding notes
- **TestCaseNotesUpdate**: Note updates
- **TestCaseNotesDelete**: Note deletion
- **TestCaseNotesRevisions**: Note revision history and management
- **TestCaseNotesSearch**: Note search functionality
- **TestCaseNotesDirectories**: Directory CRUD operations
- **TestCaseNotesComments**: Complete comment CRUD operations

**Key Coverage:**
- Note CRUD operations
- Revision tracking and history
- Note search with title and content
- Directory hierarchy management
- Parent directory validation
- Comment lifecycle for notes

### 6. test_case_rfiles_routes.py (319 lines)
Tests for evidence routes (`case_rfiles_routes.py`):
- **TestCaseEvidencesPage**: Evidences page rendering
- **TestCaseEvidencesList**: Evidence listing
- **TestCaseEvidencesState**: Evidence state management
- **TestCaseEvidencesAdd**: Adding evidences with modals
- **TestCaseEvidencesView**: Single evidence viewing
- **TestCaseEvidencesUpdate**: Evidence updates
- **TestCaseEvidencesDelete**: Evidence deletion
- **TestCaseEvidencesExcelUpload**: Excel upload functionality
- **TestCaseEvidencesComments**: Complete comment CRUD operations

**Key Coverage:**
- Evidence CRUD operations
- Excel upload with validation
- External ID tracking
- Evidence type validation
- File metadata (hash, size, description)
- Comment lifecycle for evidences

### 7. test_case_timeline_routes.py (518 lines)
Tests for timeline/event routes (`case_timeline_routes.py`):
- **TestCaseTimelinePage**: Timeline and visualization pages
- **TestCaseTimelineTimezone**: Timezone selection and conversion
- **TestCaseTimelineState**: Timeline state management
- **TestCaseTimelineEventsList**: Event listing with filters
- **TestCaseTimelineVisualize**: Timeline visualization by asset/category
- **TestCaseTimelineAdvancedFilter**: Advanced filtering with query string
- **TestCaseTimelineEventsAdd**: Adding events with modals
- **TestCaseTimelineEventsView**: Single event viewing
- **TestCaseTimelineEventsUpdate**: Event updates
- **TestCaseTimelineEventsDelete**: Event deletion
- **TestCaseTimelineEventsDuplicate**: Event duplication
- **TestCaseTimelineEventsFlag**: Event flagging
- **TestCaseTimelineEventsUpload**: CSV and Excel upload
- **TestCaseTimelineConvertDate**: Date format conversion
- **TestCaseTimelineFilterHelp**: Filter help modal
- **TestCaseTimelineEventsComments**: Complete comment CRUD operations

**Key Coverage:**
- Event CRUD operations
- Timezone handling and conversion
- Event date validation with timezone offsets
- Advanced filtering (by asset, IOC, date range, tags, etc.)
- CSV and Excel bulk upload
- Event duplication and flagging
- Asset and IOC linking to events
- Event categories
- Comment lifecycle for events
- Date format parsing and conversion

### 8. test_case_graphs_routes.py (68 lines)
Tests for graph routes (`case_graphs_routes.py`):
- **TestCaseGraphPage**: Graph page rendering
- **TestCaseGraphData**: Graph data retrieval with nodes and edges

**Key Coverage:**
- Graph visualization data structure
- Nodes (assets and IOCs)
- Edges (relationships between entities)
- Date grouping for timeline
- Empty case handling

### 9. test_case_comments.py (147 lines)
Tests for comment utility (`case_comments.py`):
- **TestCaseCommentUpdate**: Comment update functionality
- **TestCommentCrossObjectTypes**: Comments across all object types (IOC, asset, task, evidence, note, event)
- **TestCommentModals**: Comment modal rendering for all types

**Key Coverage:**
- Comment update validation
- Cross-object type comment support
- Comment CRUD operations across all entities
- Parametrized tests for all object types

## Test Patterns and Best Practices

### Fixtures Used
- `client`: Unauthenticated test client
- `authenticated_client`: Test client logged in as test user
- `admin_client`: Test client logged in as admin
- `api_headers`: Headers for API requests

### Test Structure
All tests follow the **Arrange-Act-Assert** pattern:
```python
def test_example(self, authenticated_client):
    # Arrange: Set up test data
    
    # Act: Perform the action
    response = authenticated_client.get('/case/endpoint?cid=1')
    
    # Assert: Verify the results
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
```

### Coverage Areas

#### Authentication & Authorization
- All routes test unauthenticated access (expect 302/401)
- Read operations test with `authenticated_client`
- Write operations test with `admin_client` (full access)
- Access control decorators tested: `@ac_case_requires`, `@ac_api_case_requires`

#### HTTP Methods
- GET: List, view, fetch operations
- POST: Create, update, delete operations
- All appropriate methods tested for each endpoint

#### Success Cases
- Valid data submission
- Proper response status codes (200)
- Correct response structure validation
- Data field verification

#### Error Cases
- Invalid case IDs (99999)
- Invalid object IDs
- Missing required fields
- Invalid data types
- Validation errors
- Inconsistent IDs

#### Edge Cases
- Empty data
- Duplicate entries
- Invalid CSV/Excel formats
- Missing CSV headers
- Invalid date formats
- Legacy field handling (task_assignee_id)

#### State Management
- State endpoints tested for all entities
- State tracking on CRUD operations

#### Comments
- Comment CRUD tested for all parent objects
- Comment modals tested
- Cross-object type support verified
- Parametrized tests for consistency

### Parametrized Tests
Extensive use of `@pytest.mark.parametrize` for:
- Review actions (start, cancel, request, done, etc.)
- Object types for comments (IOC, asset, task, evidence, note, event)
- Multiple similar scenarios

## Running the Tests

### Run all case blueprint tests:
```bash
pytest source/tests/unit/blueprints/case/
```

### Run specific test file:
```bash
pytest source/tests/unit/blueprints/case/test_case_routes.py
```

### Run specific test class:
```bash
pytest source/tests/unit/blueprints/case/test_case_routes.py::TestCaseSummary
```

### Run specific test:
```bash
pytest source/tests/unit/blueprints/case/test_case_routes.py::TestCaseSummary::test_summary_update_success
```

### Run with verbose output:
```bash
pytest source/tests/unit/blueprints/case/ -v
```

### Run with coverage:
```bash
pytest source/tests/unit/blueprints/case/ --cov=app.blueprints.case --cov-report=html
```

## Test Statistics

- **Total Lines**: ~2,990 lines of test code
- **Test Files**: 9 files
- **Route Files Covered**: 9 files
  1. case_routes.py
  2. case_ioc_routes.py
  3. case_assets_routes.py
  4. case_rfiles_routes.py
  5. case_tasks_routes.py
  6. case_notes_routes.py
  7. case_timeline_routes.py
  8. case_graphs_routes.py
  9. case_comments.py

- **Estimated Test Count**: 300+ individual test functions
- **Test Classes**: 65+ test classes

## Coverage Highlights

✅ **Complete CRUD Operations** for:
- Cases
- IOCs
- Assets
- Tasks
- Notes
- Evidences
- Timeline Events
- Directories

✅ **Comment System** fully tested across all entities

✅ **Upload Functionality**:
- CSV upload (IOCs, Assets, Events)
- Excel upload (Evidences, Events)
- Header detection and validation

✅ **Access Control**:
- Read-only vs full access
- Group access management
- User access management
- Case-level permissions

✅ **State Management**:
- State tracking for all entities
- State retrieval endpoints

✅ **Advanced Features**:
- Timeline filtering and visualization
- Graph data generation
- Date format conversion
- Timezone handling
- Review workflow
- Event duplication and flagging
- Note revisions
- Directory hierarchy

✅ **Error Handling**:
- Invalid IDs
- Missing data
- Validation errors
- Permission errors
- Legacy field rejection

## Notes

- Tests are designed to work with existing fixtures in `conftest.py`
- Tests handle cases where test data may not exist (accept multiple status codes)
- All tests follow project testing guidelines from `knowledge-base/testing/testing-python.md`
- No external APIs are mocked (only internal business logic tested)
- Flask framework and database interactions are not mocked per guidelines
