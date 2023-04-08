"""SQLAlchemy database management."""

# region Dependencies
# from datetime import date, datetime, timedelta
from time import sleep
from sqlalchemy.orm import sessionmaker
from .models import Base, User
from sqlalchemy import create_engine
# from typing import List, Union, Tuple
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from psycopg2 import OperationalError as psycopg2OpError
# endregion


class DBManager:
    """Project database manager."""

    def __init__(self,
                 pg_user: str,
                 pg_pass: str,
                 pg_host: str,
                 pg_port: str,
                 pg_db: str,
                 log=None):
        """Initialize the database manager.

        Pass PostgreSQL user, its password, host, and port, as well as
        the database to be managed.
        """
        self.pg_user = pg_user
        self.pg_pass = pg_pass
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_db = pg_db
        self.log = log
        connected = False
        while not connected:
            try:
                self._connect()
            except (sqlalchemyOpError, psycopg2OpError):
                sleep(2)
            else:
                connected = True
        self._update_db()

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        self._close()

    # region Connection setup
    def _connect(self) -> None:
        """Connect to the postgresql database."""
        self.engine = create_engine(f'postgresql+psycopg2://{self.pg_user}:\
{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}',
                                    pool_pre_ping=True)
        Base.metadata.bind = self.engine
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def _close(self) -> None:
        """Close the database connection."""
        self.session.close_all()

    def _recreate_tables(self) -> None:
        """Recreate tables in the database."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def _update_db(self) -> None:
        """Create the database structure if it doesn't exist (update)."""
        # Create the tables if they don't exist
        Base.metadata.create_all(self.engine)
    # endregion

    def is_user(self, user_email: str) -> bool:
        """Check if the user exists in the database."""
        return (self.session
                .query(User)
                .filter_by(email=user_email)
                .first()
                is not None)

    def add_user(self,
                 email: str,
                 password_hash: str,
                 name: str,
                 surname: str):
        """Add a user to the database."""
        user = User(email=email,
                    password_hash=password_hash,
                    first_name=name,
                    last_name=surname)
        self.session.add(user)
        self.session.commit()

    def get_user(self, user_email: str) -> User | None:
        """Get the user from the database."""
        return self.session.query(User).filter_by(email=user_email).first()

    def get_password_hash(self, user_email: str) -> str:
        """Get password hash stored in the database."""
        user = (self.session
                .query(User)
                .filter_by(email=user_email)
                .first())
        assert user is not None  # noset
        return (user.password_hash)

    def get_user_id(self, user_email: str) -> int:
        """Get the user id from the database."""
        user = (self.session
                .query(User)
                .filter_by(email=user_email)
                .first())
        assert user is not None  # noset
        return user.id

    def update_user_password(self, user_email: str, password_hash: str):
        """Update the user password in the database."""
        user = self.session.query(User).filter_by(email=user_email).first()
        assert user is not None  # noset
        user.password_hash = password_hash
        self.session.commit()

    def update_user_email(self, user_email: str, new_email: str):
        """Update the user email in the database."""
        user = self.session.query(User).filter_by(email=user_email).first()
        assert user is not None  # noset
        user.email = new_email
        self.session.commit()

    def update_user_first_name(self, user_email: str, name: str):
        """Update the user name in the database."""
        user = self.session.query(User).filter_by(email=user_email).first()
        assert user is not None  # noset
        user.first_name = name
        self.session.commit()

    def update_user_last_name(self, user_email: str, surname: str):
        """Update the user surname in the database."""
        user = self.session.query(User).filter_by(email=user_email).first()
        assert user is not None  # noset
        user.last_name = surname
        self.session.commit()
