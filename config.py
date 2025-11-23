from os import getenv
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except Exception:
    DOTENV_AVAILABLE = False


def get_db_uri():
    """Return a SQLAlchemy-compatible database URI.

    Priority order:
    1. `DATABASE_URL` environment variable (if set)
    2. Constructed from `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`

    Returns:
        str: a database URI usable by SQLAlchemy (e.g. mysql+pymysql://user:pass@host:port/db)
    """
    env_path = Path('.') / '.env'
    if DOTENV_AVAILABLE and env_path.exists():
        load_dotenv(env_path)

    db_url = getenv('DATABASE_URL')
    if db_url:
        return db_url

    user = getenv('MYSQL_USER', 'root')
    password = getenv('MYSQL_PASSWORD', '')
    host = getenv('MYSQL_HOST', 'localhost')
    port = getenv('MYSQL_PORT', '3306')
    db = getenv('MYSQL_DATABASE', 'football_db')

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"


if __name__ == '__main__':
    # Quick manual test: run `python config.py` to print the computed URI
    print(get_db_uri())
