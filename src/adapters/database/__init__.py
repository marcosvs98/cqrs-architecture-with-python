from elasticsearch import Elasticsearch, AsyncElasticsearch
import settings

def get_event_store():
    return AsyncElasticsearch([settings.ELASTICSEARCH_ENDPOINT])