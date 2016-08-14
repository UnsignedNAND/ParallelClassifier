from data.db import Db, Models


def classificate():
    Db.init()
    session = Db.create_session()
    docs = session.query(Models.Doc).filter(Models.Doc.id == 1)
    for doc in docs:
        print(doc.title)


if __name__ == '__main__':
    classificate()
