from sqlalchemy import Column, Integer, UnicodeText, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker
from utils.config_manager import get_conf
from utils.logger import get_logger

conf = get_conf()
logger = get_logger()
Base = declarative_base()


class Page(Base):
    # This table holds all pages read from Wikipedia database that was dumped
    #  into XML file.
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
    # This table holds structures of processed pages.
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
    # This table holds records of all pages that were redirecting
    __tablename__ = 'redirect'
    id = Column(Integer,
                primary_key=True)
    target = Column(UnicodeText(250),
                    nullable=False)
    title = Column(UnicodeText(250),
                   nullable=False)


class OccurrenceCount(Base):
    # This table holds information on how many times given word occurred in
    # all documents
    __tablename__ = 'occurrence_count'
    id = Column(Integer,
                primary_key=True)
    name = Column(String(48),
                  nullable=False)
    count = Column(Integer,
                   nullable=False)


class OccurrenceDocument(Base):
    # This table holds relation, that tells us if given word occurred in
    # given document
    __tablename__ = 'occurrence_document'
    id = Column(Integer,
                primary_key=True)
    word_id = Column(Integer,
                     ForeignKey('occurrence_count.id'),
                     nullable=False)
    document_id = Column(Integer,
                         ForeignKey("page.id"),
                         nullable=False)


def delete():
    Base.metadata.bind = engine
    db_delete_session = sessionmaker(bind=engine)
    delete_session = db_delete_session()
    clear_tables = [OccurrenceDocument, OccurrenceCount, Redirect,
                    ProcessedPage, Page]
    try:
        for clear_table in clear_tables:
            logger.debug("Deleted {0} rows from {1}".format(
                delete_session.query(
                clear_table).delete(), str(clear_table.__tablename__)))
        delete_session.commit()
    except:
        delete_session.rollback()
        raise

engine = create_engine(conf['db']['connection'])
Base.metadata.create_all(engine)

if __name__ == '__main__':
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()

    pages = session.query(Page).all()
    for page in pages:
        print(page.title)
