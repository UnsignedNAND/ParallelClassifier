from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class Page(Base):
    __tablename__ = 'page'
    title = Column(String(250), nullable=False, primary_key=True)
    redirect = Column(String(250), ForeignKey('page.title'), nullable=True)
    text = Column(UnicodeText, nullable=False)

engine = create_engine('sqlite:///wiki.db')
Base.metadata.create_all(engine)
