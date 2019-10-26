def handle(req):
    if not req.startswith('My request:'):
        return 'Invalid request!: ' + req
    else:
        r = req.replace('My request:', '', 1)
        result = r.upper()
        return result

