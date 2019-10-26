import os

def handle(req):
    ckan_host = os.getenv('CKAN_HOST', None)
    ckan_port = os.getenv('CKAN_PORT', None)
    return { 'HOST': ckan_host,
             'PORT': ckan_port }

