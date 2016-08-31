import multiprocessing


class Parser(multiprocessing.Process):
    def __init__(self, queue_unparsed_docs, pipe_tokens_to_idf_child,
                 event, pipe_tokens_to_processes_child, queue_parsed_docs):
        self._queue_unparsed_docs = queue_unparsed_docs
        self._pipe_tokens_to_idf_child = pipe_tokens_to_idf_child
        self._event = event
        self._pipe_tokens_to_processes_child = \
            pipe_tokens_to_processes_child
        self._queue_parsed_docs = queue_parsed_docs
        super(self.__class__, self).__init__()
        self.parsed_pages_num = 0

    def _process_page(self):
        page = self._queue_unparsed_docs.get()
        if page is None:
            return None
        page.create_tokens()
        for token in page.tokens:
            self._pipe_tokens_to_idf_child.send(token.stem)
        page.content_clean()
        self.parsed_pages_num += 1
        return page

    def _signal_end_processing(self):
        # Just to be sure that other threads can also take a pill
        self._queue_unparsed_docs.put(None)
        self._pipe_tokens_to_idf_child.send(None)
        print('Process {0} finished after processing {1} '
              'docs'.format(self.pid, self.parsed_pages_num))

    def _tfidf(self, parsed_pages):
        print('Process {0} waiting on IDF to finish...'.format(self.pid))
        self._event.wait()
        recv_tokens = self._pipe_tokens_to_processes_child.recv()
        print('Process {0} received {1} tokens from IDF'.format(
            self.pid, len(recv_tokens)))
        for page in parsed_pages:
            for token in page.tokens:
                try:
                    token.idf = recv_tokens[token.stem]
                    page.tfidf[token.stem] = token.calc_tf_idf()
                except KeyError as ke:
                    print('error', token)
            self._queue_parsed_docs.put(page)
        # sending process-end pill
        self._queue_parsed_docs.put(None)

    def run(self):
        self.parsed_pages_num = 0
        parsed_pages = []
        while True:
            page = self._process_page()
            if page:
                parsed_pages.append(page)
            else:
                self._signal_end_processing()
                break

        self._tfidf(parsed_pages)


def create_parsers(queue_unparsed_documents,
                   pipe_tokens_to_idf_child,
                   event,
                   pipes_tokens_to_processes_child,
                   queue_parsed_docs,
                   process_num):
    processes = []
    for i in range(process_num):
        process = Parser(
            queue_unparsed_docs=queue_unparsed_documents,
            pipe_tokens_to_idf_child=pipe_tokens_to_idf_child,
            event=event,
            pipe_tokens_to_processes_child=pipes_tokens_to_processes_child[i],
            queue_parsed_docs=queue_parsed_docs
        )
        processes.append(process)
    return processes
