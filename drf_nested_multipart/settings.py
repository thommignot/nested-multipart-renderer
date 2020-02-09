"""
Add the NestedMultiPartRenderer class and nestedmultipart format
to the default TEST_REQUEST_RENDERER_CLASSES rest_framework settings
"""
from rest_framework import settings

settings.DEFAULTS['TEST_REQUEST_RENDERER_CLASSES'].append(
    'drf_nested_multipart.renderers.NestedMultiPartRenderer'
)
