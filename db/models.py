from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker
import atexit
import datetime


con_string = 'sqlite:///db/database.db'

engine = create_engine(con_string)
Session = sessionmaker(bind=engine, expire_on_commit=False)

atexit.register(engine.dispose)


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = 'post'
    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
    imgs: Mapped[str] = mapped_column(nullable=True)
    site: Mapped[str] = mapped_column(nullable=True)
    tag: Mapped[str] = mapped_column(nullable=True)
    time_public: Mapped[datetime.datetime] = mapped_column(nullable=True)
    time_stamp: Mapped[datetime.datetime] = mapped_column(nullable=True)


def create_tables():
    Base.metadata.create_all(engine)
