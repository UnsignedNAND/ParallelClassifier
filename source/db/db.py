from sqlalchemy import Column, Integer, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer,
                primary_key=True)
    title = Column(UnicodeText(250))
    redirect = Column(UnicodeText(250),
                      nullable=True)
    text = Column(UnicodeText,
                  nullable=False)
    parsed_text = Column(UnicodeText,
                         nullable=True)


class Redirect(Base):
    __tablename__ = 'redirect'
    id = Column(Integer,
                primary_key=True)
    target = Column(UnicodeText(250),
                    nullable=False)
    title = Column(UnicodeText(250),
                   nullable=False)

engine = create_engine('mysql://root:r00tme@localhost/wiki')
Base.metadata.create_all(engine)


if __name__ == '__main__':
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()

    pages = session.query(Page).all()
    for page in pages:
        print page.title
