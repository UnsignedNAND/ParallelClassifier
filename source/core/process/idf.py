import math
import multiprocessing

from data.db import Db, Models
from utils.config import get_conf
from utils.general import str2bool

CONF = get_conf()


class IDF(multiprocessing.Process):
    def __init__(self, pipe_tokens_to_idf_parent, docs_num, event,
                 pipes_tokens_to_processes_parent, process_num):
        self._pipe_tokens_to_idf_parent = pipe_tokens_to_idf_parent
        self._docs_num = docs_num  # total number of documents
        self._event = event
        self._tokens = {}
        self._pipes_tokens_to_processes_parent = \
            pipes_tokens_to_processes_parent
        self.process_num = process_num
        super(self.__class__, self).__init__()

    def run(self):
        session = None
        token_counter = None
        if str2bool(CONF['general']['save_to_db']):
            Db.init()
            session = Db.create_session()
            token_counter = 0

        pills = 0
        while pills < self.process_num:
            msg = self._pipe_tokens_to_idf_parent.recv()
            if msg is None:
                pills += 1
                continue
            if msg in self._tokens.keys():
                self._tokens[msg] += 1
            else:
                self._tokens[msg] = 1

        for token in self._tokens:
            # IDF(token) = 1 + log_e(Total Number Of Documents / Number Of
            # Documents with token in it)
            token_idf = 1 + math.log(self._docs_num / self._tokens[token],
                                     math.e)
            self._tokens[token] = token_idf

            if str2bool(CONF['general']['save_to_db']):
                token_counter += 1
                t = Models.Token()
                t.stem = token
                t.idf = token_idf
                session.add(t)

                if token_counter % 50 == 0:
                    session.commit()
        if str2bool(CONF['general']['save_to_db']):
            session.commit()
        self._event.set()
        for pipe in self._pipes_tokens_to_processes_parent:
            pipe.send(self._tokens)
        print('IDF sent {0} tokens'.format(len(self._tokens)))