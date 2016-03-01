from sqlalchemy import Column, Integer, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker
from utils.config_manager import get_conf

conf = get_conf()
Base = declarative_base()


class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer,
                primary_key=True)
    title = Column(UnicodeText(250),
                   nullable=False)
    redirect = Column(UnicodeText(250),
                      nullable=True)
    text = Column(UnicodeText,
                  nullable=False)


class ProcessedPage(Base):
    __tablename__ = 'processed_page'
    id = Column(Integer,
                primary_key=True)
    page_id = Column(Integer,
                     ForeignKey("page.id"),
                     nullable=False)
    parsed_title = Column(UnicodeText(250),
                          nullable=False)
    parsed_text = Column(UnicodeText,
                         nullable=False)


class Redirect(Base):
    __tablename__ = 'redirect'
    id = Column(Integer,
                primary_key=True)
    target = Column(UnicodeText(250),
                    nullable=False)
    title = Column(UnicodeText(250),
                   nullable=False)


class Occurrence(Base):
    __tablename__ = 'occurrence'
    id = Column(Integer,
                primary_key=True)
    name = Column(UnicodeText(48),
                  nullable=False)
    count = Column(Integer,
                   nullable=False)


engine = create_engine(conf['db']['connection'])
Base.metadata.create_all(engine)


if __name__ == '__main__':
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()

    pages = session.query(Page).all()
    for page in pages:
        print page.title
