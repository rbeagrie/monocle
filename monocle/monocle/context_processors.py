def header(request):
    from settings import MONOCLE_VERSION
    return {'monocle_version': MONOCLE_VERSION}