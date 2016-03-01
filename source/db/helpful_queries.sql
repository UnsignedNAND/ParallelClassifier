# Queries in this file might be outdated and as a result do not work.
# Treat as an example.

SELECT c.name, p.parsed_title FROM occurrence_document o
    INNER JOIN processed_page p ON o.document_id = p.page_id
    INNER JOIN occurrence_count c ON o.word_id = c.id;