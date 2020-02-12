"""This module loads all jsonschemas."""

import json
import os


def _load_jsonschema(schema_name):
    filename = os.path.join(
        os.path.dirname(__file__),
        'jsonschemas',
        '%s.json' % schema_name)

    with open(filename) as fp:
        return json.load(fp)


spider_metadata = _load_jsonschema('spider_metadata')

crawl_result = _load_jsonschema('crawl_result')
