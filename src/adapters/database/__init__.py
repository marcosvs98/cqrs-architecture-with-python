from elasticsearch import Elasticsearch, AsyncElasticsearch


def get_event_store():
    return AsyncElasticsearch(['http://elasticsearch:9200'])