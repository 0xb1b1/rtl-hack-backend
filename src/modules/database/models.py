"""Models for SQLAlchemy."""
import enum
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, BigInteger, Text, TypeDecorator
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# region Enums
class CompanyClearance(enum.IntEnum):
    """User-to-company access types."""

    admin = 0
    editor = 1
    viewer = 2
# endregion


# region Custom column types
class IntEnum(TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.

    The default would have stored the enum's *name* (ie the string).
    """

    impl = Integer
    cache_ok: bool = True

    def __init__(self, enumtype, *args, **kwargs):
        """Initialize."""
        # pylint: disable=bad-super-call
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        """Process bind parameter."""
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        """Process result value."""
        return self._enumtype(value)
# endregion


class User(Base):  # type: ignore
    """User model for SQLAlchemy."""

    __tablename__ = 'users'
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)
    email = Column(Text, nullable=False)
    password_hash = Column(Text, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)

    # One-to-many relationship between User and CompanyClearanceLevel
    access_levels = relationship('CompanyClearanceLevel',
                                 back_populates='user_id')


class Company(Base):  # type: ignore
    """Company model for SQLAlchemy."""

    __tablename__ = 'companies'
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)
    name = Column(Text, nullable=False)
    inn = Column(BigInteger, nullable=False)

    # One-to-many relationship between Company and CompanyClearanceLevel
    access_levels = relationship('CompanyClearanceLevel',
                                 back_populates='company_id')


class CompanyClearanceLevel(Base):  # type: ignore
    """User-to-company access level model for SQLAlchemy."""

    __tablename__ = 'access_levels'
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)
    user_id = Column(BigInteger,
                     ForeignKey('users.id'),
                     nullable=False)
    company_id = Column(BigInteger,
                        ForeignKey('companies.id'),
                        nullable=False)
    access_level: Column(IntEnum(CompanyClearance),  # type: ignore
                         nullable=False)
