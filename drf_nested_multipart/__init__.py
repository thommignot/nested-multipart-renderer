from rest_framework import settings


settings.DEFAULTS['TEST_REQUEST_RENDERER_CLASSES'] += (
    'drf_nested_multipart.renderers.NestedMultiPartRenderer',
)


__version__ = '0.2.0'
