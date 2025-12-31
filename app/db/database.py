import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from pathlib import Path
from app.core.config import settings


@contextmanager
def get_db():
    """Get database connection as a context manager."""
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database tables from schema.sql."""
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.execute(schema_sql)
        conn.commit()
