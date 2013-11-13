"""This module contains JSON schemas that can be used to validate
JSON request and response bodies between the various CLF services."""


"""```crawl_request``` is a JSON schema used to validate
messages in the crawl request queue."""
crawl_request = {
    "type": "object",
    "properties": {
        "uuid": {
            "type": "string",
            "minLength": 1,
        },
        "spider": {
            "type": "string",
            "minLength": 1,
        },
        "args": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "uuid",
        "spider",
        "args",
    ],
    "additionalProperties": False,
}
