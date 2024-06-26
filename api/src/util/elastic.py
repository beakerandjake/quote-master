import os
from elasticsearch import Elasticsearch


ELASTIC_SERVER_URL = os.environ.get("ELASTIC_SERVER_URL", "http://localhost:9200")
ELASTIC_INDEX = os.environ.get("ELASTIC_INDEX", "wikiquote")
ELASTIC_INDEX_URL = f"{ELASTIC_SERVER_URL}/{ELASTIC_INDEX}"
client = Elasticsearch(ELASTIC_SERVER_URL)


def get_stats():
    """Returns the total number of documents"""
    result = client.indices.stats(index=ELASTIC_INDEX)
    return {
        "number_of_docs": result["_all"]["primaries"]["docs"]["count"],
        "size_in_bytes": result["_all"]["primaries"]["store"]["size_in_bytes"],
    }


def _map_results(results):
    """Extracts the necessary information from the raw elasticsearch results."""
    return {
        "total": results["hits"]["total"]["value"],
        "top": [item["_source"] for item in results["hits"]["hits"]],
    }


def search_exact(terms: list[str]):
    """Returns all documents which match the terms exactly"""
    results = client.search(
        index=ELASTIC_INDEX,
        query={"match_phrase": {"text": {"query": " ".join(terms)}}},
        source=["title", "page_id"],
    )
    return _map_results(results)


def search_forgiving(terms: list[str]):
    """Returns all documents which contain all of the terms"""
    results = client.search(
        index=ELASTIC_INDEX,
        query={"match": {"text": {"query": " ".join(terms), "operator": "and"}}},
        source=["title", "page_id"],
    )
    return _map_results(results)
