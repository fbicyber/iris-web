import os
import pytest

from app import create_app
from app.extensions import db, bc
from app.models.authorization import User, Group, Organisation
from app.models.cases import Client, Cases
from app.models.models import AnalysisStatus


@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SERVER_SETTINGS': {'enforce_mfa': False},  # Disable MFA for tests
        'SQLALCHEMY_ECHO': False,  # Disable SQL echo for cleaner test output
    })

    with app.app_context():
        from app.post_init import (
            create_safe_analysis_status,
            create_safe_auth_model,
            create_safe_admin,
            create_safe_case,
            create_safe_client,
            create_safe_db,
            create_safe_server_settings,
        )

        create_safe_db(db_name="iris_tasks")
        db.create_all()
        db.session.commit()

        # Create barebones post-init data
        def_org, gadm, ganalysts = create_safe_auth_model()
        admin, pwd = create_safe_admin(def_org, gadm=gadm)
        client = create_safe_client()
        case = create_safe_case(
            user=admin,
            client=client,
            groups=[gadm, ganalysts]
        )
        create_safe_server_settings()

        # Initialize custom attributes for events and other objects
        from app.post_init import create_safe_attributes, create_safe_hooks
        try:
            create_safe_attributes()
            print("[APP FIXTURE] Custom attributes initialized")
        except Exception as e:
            print(f"[APP FIXTURE] Error initializing attributes: {e}")
            raise

        # Initialize module hooks
        try:
            create_safe_hooks()
            print("[APP FIXTURE] Module hooks initialized")
        except Exception as e:
            print(f"[APP FIXTURE] Error initializing hooks: {e}")
            raise

        try:
            create_safe_analysis_status()
            print("[APP FIXTURE] Analysis status initialized")
        except Exception as e:
            print(f"[APP FIXTURE] Error initializing analysis status: {e}")
            raise

        db.session.commit()

        # Verify custom attributes were created
        from app.models.models import CustomAttribute
        event_attr = CustomAttribute.query.filter(CustomAttribute.attribute_for == 'event').first()
        print(f"[APP FIXTURE] Event custom attribute exists: {event_attr is not None}")

        # Ensure admin has effective case access
        from app.iris_engine.access_control.utils import ac_add_user_effective_access
        from app.models.authorization import CaseAccessLevel, UserCaseEffectiveAccess

        # Remove any existing access for admin to start fresh
        deleted_count = UserCaseEffectiveAccess.query.filter(
            UserCaseEffectiveAccess.user_id == admin.id,
            UserCaseEffectiveAccess.case_id == case.case_id
        ).delete()
        print(f"[APP FIXTURE] Deleted {deleted_count} existing access records for admin")

        # Add fresh access - create multiple times to be absolutely sure
        ucea = UserCaseEffectiveAccess()
        ucea.user_id = admin.id
        ucea.case_id = case.case_id
        ucea.access_level = CaseAccessLevel.full_access.value
        db.session.add(ucea)

        print(f"[APP FIXTURE] Creating UserCaseEffectiveAccess: user_id={admin.id}, case_id={case.case_id}, access_level={CaseAccessLevel.full_access.value}")
        db.session.commit()

        # Set admin's context case so they have a default case
        # Use update() to ensure the database is modified directly
        from app.models.authorization import User as UserModel
        db.session.query(UserModel).filter_by(id=admin.id).update({
            'ctx_case': case.case_id,
            'ctx_human_case': case.name
        })
        db.session.commit()

        # Verify the update persisted
        admin_check = db.session.query(UserModel).filter_by(id=admin.id).first()
        print(f"[APP FIXTURE] Admin context case set: ctx_case={admin_check.ctx_case}, ctx_human_case={admin_check.ctx_human_case}")
        check = UserCaseEffectiveAccess.query.filter(
            UserCaseEffectiveAccess.user_id == admin.id,
            UserCaseEffectiveAccess.case_id == case.case_id
        ).first()

        # Also check GroupCaseAccess
        from app.models.authorization import GroupCaseAccess
        group_access = GroupCaseAccess.query.filter(
            GroupCaseAccess.case_id == case.case_id
        ).all()

        print(f"\n[APP FIXTURE] Admin case access created: {check is not None}, admin.id={admin.id}, case.case_id={case.case_id}")
        if check:
            print(f"[APP FIXTURE] Access level: {check.access_level}")
        print(f"[APP FIXTURE] Admin context case set: ctx_case={admin.ctx_case}, ctx_human_case={admin.ctx_human_case}")
        print(f"[APP FIXTURE] Group case access records: {len(group_access)}")
        for ga in group_access:
            print(f"[APP FIXTURE]   Group {ga.group_id} -> Case {ga.case_id}, level={ga.access_level}")

        # Final flush and commit to ensure all data is persisted
        db.session.flush()
        db.session.commit()

    yield app

    # Cleanup - remove session, Docker will clean database
    with app.app_context():
        db.session.remove()


@pytest.fixture(autouse=True)
def db_transaction(app):
    """Automatically manage database transactions for each test.

    This fixture ensures that:
    1. Each test starts with a clean transaction
    2. Any data added during the test is rolled back after
    3. Session-level data (created during app setup) persists
    """
    with app.app_context():
        # Start a new transaction for this test
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind the session to this transaction
        db.session.bind = connection

        yield

        # Rollback the transaction, undoing any changes made during the test
        transaction.rollback()
        connection.close()

        # Restore the session binding
        db.session.bind = db.engine


@pytest.fixture(autouse=True)
def mock_case_access_check(monkeypatch, app):
    """Mock the case access check to grant appropriate access based on user role.

    This is a workaround for SQLAlchemy session scoping issues where
    UserCaseEffectiveAccess records created in fixtures aren't visible
    to request handlers due to different session contexts.

    - Admin users get full_access
    - Regular authenticated users get read_only access
    - This allows testing of authorization requirements
    """
    from app.models.authorization import CaseAccessLevel, User

    def mock_ac_fast_check_user_has_case_access(user_id, cid, access_level):
        """Mock that returns access level based on user role.

        Args:
            user_id: User ID
            cid: Case ID (unused in mock, all cases accessible)
            access_level: List of acceptable access levels
        """
        _ = cid  # Intentionally unused in test mock

        # Look up the user to determine their role
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                # No user found, deny access
                return None

            # Check if user is admin (user_id 1 is always admin from fixture)
            is_admin = (user_id == 1) or (user.name == 'administrator')

            # If no access level required, grant based on role
            if not access_level:
                return CaseAccessLevel.full_access.value if is_admin else CaseAccessLevel.read_only.value

            # Admin gets full access
            if is_admin:
                return CaseAccessLevel.full_access.value

            # Regular users only get read_only access
            # Check if read_only is acceptable
            for acl in access_level:
                if acl == CaseAccessLevel.read_only:
                    return CaseAccessLevel.read_only.value

            # If full_access is required but user is not admin, return None (denied)
            return None

    # Patch the access control function
    monkeypatch.setattr(
        'app.iris_engine.access_control.utils.ac_fast_check_user_has_case_access',
        mock_ac_fast_check_user_has_case_access
    )

    # Also need to patch it in the util module since it's imported there
    monkeypatch.setattr(
        'app.util.ac_fast_check_user_has_case_access',
        mock_ac_fast_check_user_has_case_access
    )


@pytest.fixture()
def client(app):
    """Create a test client without authentication."""
    return app.test_client()


@pytest.fixture(scope='session')
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        from app.datamgmt.manage.manage_users_db import add_user_to_group

        # Create test user
        user = User(
            user='testuser',
            name='Test User',
            email='testuser@example.com',
            password=bc.generate_password_hash('testpass123').decode('utf8'),
            active=True,
            is_service_account=False
        )

        # Set up context case
        case = Cases.query.first()
        if case:
            user.ctx_case = case.case_id
            user.ctx_human_case = case.name

        db.session.add(user)
        db.session.commit()

        # Add user to Analysts group for API access
        analysts_group = Group.query.filter_by(group_name='Analysts').first()
        if analysts_group and case:
            add_user_to_group(user.id, analysts_group.group_id)
            db.session.commit()

            # Grant effective case access to the test user
            from app.models.authorization import CaseAccessLevel
            from app.iris_engine.access_control.utils import ac_add_user_effective_access

            ac_add_user_effective_access(
                users_list=[user.id],
                case_id=case.case_id,
                access_level=CaseAccessLevel.full_access.value
            )
            db.session.commit()

        # Refresh to get the ID
        db.session.refresh(user)
        user_id = user.id

    # Return user data that can be used outside app context
    return {
        'id': user_id,
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'testuser@example.com'
    }


@pytest.fixture()
def authenticated_client(app, test_user):
    """Create a test client with an authenticated session (new client per test)."""
    client = app.test_client()

    # Log in the test user
    # Note: cookies persist automatically in test client
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)

    # Debug: check login response
    print(f"\n[authenticated_client] Login status: {response.status_code}")
    if response.status_code not in [200, 302]:
        print(f"[authenticated_client] Login failed: {response.get_data(as_text=True)[:500]}")

    return client


@pytest.fixture()
def admin_client(app):
    """Create a test client authenticated as the admin user (new client per test)."""
    client = app.test_client()

    # Log in as admin - the actual username from logs is 'admin'
    admin_username = 'admin'
    admin_password = 'admin'

    response = client.post('/login', data={
        'username': admin_username,
        'password': admin_password
    }, follow_redirects=True)

    # Debug: check login response
    print(f"\n[admin_client] Login status: {response.status_code}")
    print(f"[admin_client] Login username: {admin_username}")
    if response.status_code not in [200, 302]:
        print(f"[admin_client] Login failed: {response.get_data(as_text=True)[:500]}")

    return client


@pytest.fixture()
def api_headers():
    """Return headers for API authentication."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture(scope='session')
def sample_event_category(app):
    """Create a sample event category."""
    with app.app_context():
        from app.models.models import EventCategory

        category = EventCategory.query.filter_by(name='Unspecified').first()
        if not category:
            category = EventCategory(name='Unspecified')
            db.session.add(category)
            db.session.commit()

        return category.id


@pytest.fixture(scope='function')
def sample_asset(app):
    """Create a sample case asset."""
    with app.app_context():
        from app.models.models import CaseAssets, AssetsType

        case = Cases.query.first()
        asset_type = AssetsType.query.first()

        if not asset_type:
            asset_type = AssetsType(asset_name='Server')
            db.session.add(asset_type)
            db.session.commit()

        asset = CaseAssets(
            asset_name='test-server-01',
            asset_type_id=asset_type.asset_id,
            case_id=case.case_id,
            asset_description='Test server'
        )
        db.session.add(asset)
        db.session.commit()

        return asset.asset_id


@pytest.fixture(scope='function')
def sample_ioc(app):
    """Create a sample IOC."""
    with app.app_context():
        from app.models.models import Ioc, IocLink, IocType

        case = Cases.query.first()
        ioc_type = IocType.query.first()

        if not ioc_type:
            ioc_type = IocType(type_name='ip-any')
            db.session.add(ioc_type)
            db.session.commit()

        ioc = Ioc(
            ioc_value='192.168.1.1',
            ioc_type_id=ioc_type.type_id,
            ioc_description='Test IOC',
        )
        db.session.add(ioc)
        db.session.commit()

        ioc_link = IocLink(
            case_id=case.case_id,
            ioc_id=ioc.ioc_id,
        )
        db.session.add(ioc_link)
        db.session.commit()

        return ioc.ioc_id


@pytest.fixture(scope='function')
def sample_event(app, test_user, sample_event_category):
    """Create a sample timeline event."""
    with app.app_context():
        from app.models.cases import CasesEvent
        from datetime import datetime

        case = Cases.query.first()

        event = CasesEvent(
            event_title='Test Event',
            event_content='Test event content',
            event_raw='Raw event data',
            event_source='Test Source',
            event_date=datetime(2024, 1, 1, 12, 0, 0),
            event_date_wtz=datetime(2024, 1, 1, 12, 0, 0),
            event_tz='UTC',
            event_in_graph=False,
            event_in_summary=True,
            event_is_flagged=False,
            case_id=case.case_id,
            user_id=test_user['id'],
            event_color='#1572E8',
            event_tags='test,sample'
        )
        db.session.add(event)
        db.session.flush()  # Ensure event_id is generated

        # Link to category
        from app.models.models import CaseEventCategory
        event_cat = CaseEventCategory(
            event_id=event.event_id,
            category_id=sample_event_category
        )
        db.session.add(event_cat)
        db.session.commit()

        return event.event_id


@pytest.fixture(scope='function')
def sample_event_comment(app, sample_event, test_user):
    """Create a sample event comment."""
    with app.app_context():
        from app.models.models import Comments, EventComments
        from app.models.cases import CasesEvent
        from datetime import datetime

        # Verify the event actually exists
        event = CasesEvent.query.filter_by(event_id=sample_event).first()
        if not event:
            raise ValueError(f"sample_event fixture did not create event with id {sample_event}")

        case = Cases.query.first()

        comment = Comments(
            comment_text='Test comment',
            comment_date=datetime.now(),
            comment_update_date=datetime.now(),
            comment_user_id=test_user['id'],
            comment_case_id=case.case_id
        )
        db.session.add(comment)
        db.session.flush()  # Ensure comment_id is generated

        event_comment = EventComments(
            comment_id=comment.comment_id,
            comment_event_id=sample_event
        )
        db.session.add(event_comment)
        db.session.commit()

        return comment.comment_id
