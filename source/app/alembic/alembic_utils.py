from alembic import op
from sqlalchemy import engine_from_config
from sqlalchemy.engine import reflection


from sqlalchemy import text


def _table_has_column(table, column):
    # Use the migration's bind so the check runs in the same session/transaction
    # as Alembic operations (avoids cross-session locking races).
    connection = op.get_bind()
    try:
        result = connection.execute(text(f"SELECT * FROM \"{table}\" LIMIT 1"))
        columns = result.keys()
    except Exception:
        return False

    has_column = column in columns
    return has_column


def _has_table(table_name):
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy."
    )
    inspector = reflection.Inspector.from_engine(engine)
    tables = inspector.get_table_names()
    return table_name in tables


def index_exists(table_name, index_name):
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy."
    )
    inspector = reflection.Inspector.from_engine(engine)
    indexes = inspector.get_indexes(table_name)
    return any(index['name'] == index_name for index in indexes)