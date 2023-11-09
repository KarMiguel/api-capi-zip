
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db.models import Base

from decouple import config as decouple_config

# Desativa o pylint pro arquivo inteiro. O alembic usa muitos metadados gerados durante runtime,
# e isso impede o pylint de verificar diversos campos

# pylint: skip-file

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata

# Importa as entidades definidas em app/entities/__init__.py. Usado para permitir a geração automática de
# revisions pelo Alembic. Se alguma mudança não estiver sendo replica no "autogenerate" do Alembic, verifique
# se o módulo relevante está sendo importado em app/entities/__init__.py.


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = decouple_config('DB_URL')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        # dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Custom config obtém a config padrão do alembic.ini e altera a URL do DB
    custom_config = config.get_section(config.config_ini_section)
    custom_config["sqlalchemy.url"] = decouple_config('DB_URL')

    connectable = engine_from_config(
        custom_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
