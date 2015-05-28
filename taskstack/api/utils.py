import json


def response_to_json(json_response=None):
    """Gets content from a JsonResponse object and converts to a dict."""
    try:
        return json.loads(json_response.content.decode('utf-8'))
    except ValueError:
        return {}