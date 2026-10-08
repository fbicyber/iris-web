from alembic import context
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app import create_app

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

import os
os.environ["ALEMBIC"] = "1"

from app.extensions import db
from app.configuration import SQLALCHEMY_BASE_ADMIN_URI, PG_DB_

# Import model modules here for autogenerate to detect them

config.set_main_option('sqlalchemy.url', SQLALCHEMY_BASE_ADMIN_URI + PG_DB_)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
app = create_app()
with app.app_context():
    import app.models.models
    import app.models.alerts
    import app.models.authorization
    import app.models.cases

    target_metadata = db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_name(name, type_, parent_names):
    if type_ == "index":
        if name in ["idx_ioc_value_hash"]:
            return False
    return True


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "index":
        # skip functional / expression indexes
        if hasattr(object, "expressions"):
            if any(getattr(expr, "name", None) is None for expr in object.expressions):
                return False
        # skip indexes with no column names (expression indexes)
        if hasattr(object, "columns"):
            if any(col.name is None for col in object.columns):
                return False
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name,
            include_object=include_object

        )
        with context.begin_transaction(): # -- Fixes stuck transaction. Need more info on that

            context.run_migrations()
            # connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
