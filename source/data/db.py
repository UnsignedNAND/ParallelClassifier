from sqlalchemy import Column, Integer, UnicodeText, create_engine
from sqlalchemy.ext.declarative import declarative_base
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
        __table_args__ = {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci'}
        id = Column(Integer,
                    primary_key=True)
        title = Column(UnicodeText(250),
                       nullable=False)
        redirect = Column(UnicodeText(250),
                          nullable=True)
        # MySQL UnicodeText default length is too short to store certain Wiki
        # pages, so it has to be defined
        text = Column(UnicodeText(320000),
                      nullable=False)


class Db:
    @staticmethod
    def _connect():
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

    @staticmethod
    def init():
        Db._connect()
        BASE.metadata.bind = ENGINE

    @staticmethod
    def create_session():
        db_session = sessionmaker(bind=ENGINE)
        return db_session()


if __name__ == '__main__':
    Db.init()
    Db.clean()
    session = Db.create_session()

    for i in range(0, 5):
        page = Models.Page()
        page.title = 'Title' + str(i)
        page.text = 'Text ' + str(i)
        session.add(page)

    session.commit()

    pages = session.query(Models.Page).all()
    for page in pages:
        print(page.id)
