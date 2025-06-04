#!/usr/bin/env python3

import os
import json
import sys
import requests
from urllib.parse import urlparse

def parse_docs(url_file):
    with open(url_file, 'r') as f:
        urls = f.read()

    for url in urls.split('\n'):
        if url is None or url == '':
            continue

        r = requests.get(url)
        apidocs = r.json()

        csv = {}
        domain = urlparse(url).hostname
        if domain not in csv:
            csv[domain] = []

        # OpenAPI 3.x
        if 'openapi' in apidocs and str(apidocs['openapi']).startswith('3.') and 'paths' in apidocs:
            for path, methods in apidocs['paths'].items():
                for method in methods:
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']:
                        csv[domain].append({"endpoint": path, "method": method.upper()})
        # Swagger 2.0
        elif 'swagger' in apidocs and str(apidocs['swagger']).startswith('2.'):
            if 'paths' in apidocs:
                for path, methods in apidocs['paths'].items():
                    for method in methods:
                        if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']:
                            csv[domain].append({"endpoint": path, "method": method.upper()})
            elif 'apis' in apidocs:
                for api in apidocs['apis']:
                    # Swagger 2.0 で 'apis' の場合は method 情報がない可能性が高い
                    csv[domain].append({"endpoint": api['path'], "method": ''})
            else:
                print("This swagger doc has no APIs defined!")
                sys.exit(1)
        # Swagger 1.x (従来のまま)
        elif 'apis' in apidocs:
            for api in apidocs['apis']:
                csv[domain].append({"endpoint": api['path'], "method": ''})
        else:
            print("This swagger/openapi doc has no APIs defined!")
            sys.exit(1)

        with open('apis.csv', 'w', encoding='utf-8') as f:
            f.write("domain,endpoint,method\n")
            for domain in csv:
                for item in csv[domain]:
                    f.write("{},{},{}\n".format(domain, item["endpoint"], item["method"]))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} [file containing URLs]".format(sys.argv[0]))
        sys.exit(1)

    parse_docs(sys.argv[1])
