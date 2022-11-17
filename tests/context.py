from asgi_correlation_id.context import correlation_id

def correlation_id_filter(record):
    record["correlation_id"] = correlation_id.get()
    return record["correlation_id"]