# Queries in this file might be outdated and as a result do not work.
# Treat as an example.

# Show words that occur in given document
SELECT c.name, p.parsed_title
    FROM occurrence_document o
    INNER JOIN processed_page p ON o.document_id = p.page_id
    INNER JOIN occurrence_count c ON o.word_id = c.id;

# Show database size.
SELECT  sum(round(((data_length + index_length) / 1024 / 1024 / 1024), 2))  as "Size in GB"
    FROM information_schema.TABLES
    WHERE table_schema = "wiki";
