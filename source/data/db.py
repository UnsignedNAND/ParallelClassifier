from sqlalchemy import Column, Integer, UnicodeText, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker
from utils.config import get_conf
from utils.log import get_log

BASE = declarative_base()
CONF = get_conf()
ENGINE = None
LOG = get_log()


class Models:
    class Page(BASE):
        # This table holds all pages read from Wikipedia database that was
        # dumped into XML file.
        __tablename__ = 'page'
        id = Column(Integer,
                    primary_key=True)
        title = Column(UnicodeText(250),
                       nullable=False)
        redirect = Column(UnicodeText(250),
                          nullable=True)
        text = Column(UnicodeText,
                      nullable=False)


class Db:
    @staticmethod
    def connect():
        global ENGINE
        global BASE
        ENGINE = create_engine(CONF['db']['connection'])
        BASE.metadata.create_all(ENGINE)

    @staticmethod
    def clean():
        global ENGINE
        global BASE
        BASE.metadata.bind = ENGINE
        db_delete_session = sessionmaker(bind=ENGINE)
        delete_session = db_delete_session()
        clear_tables = [Models.Page]
        try:
            for clear_table in clear_tables:
                LOG.debug("Deleted {0} rows from {1}".format(
                    delete_session.query(
                        clear_table).delete(), str(clear_table.__tablename__)))
            delete_session.commit()
        except:
            delete_session.rollback()
            raise


if __name__ == '__main__':
    Db.connect()
    Db.clean()
    BASE.metadata.bind = ENGINE
    db_session = sessionmaker(bind=ENGINE)
    session = db_session()

    for i in range(0, 5):
        page = Models.Page()
        page.title = 'Title' + str(i)
        page.text = 'Text ' + str(i)
        session.add(page)

    session.commit()

    pages = session.query(Models.Page).all()
    for page in pages:
        print(page.id)
