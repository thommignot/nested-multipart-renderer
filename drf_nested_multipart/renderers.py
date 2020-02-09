"""
Renderers are used to serialize a response into specific media types.

They give us a generic way of being able to handle various media types
on the response.

The NestedMultipartRenderer renders complex/nested objects into
multipart/form-data format.
"""
from rest_framework.renderers import BaseRenderer
from drf_nested_multipart.utils import encoders


class NestedMultiPartRenderer(BaseRenderer):
    media_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
    format = 'nestedmultipart'
    charset = 'utf-8'
    BOUNDARY = 'BoUnDaRyStRiNg'

    def render(self, data, media_type=None, renderer_context=None):
        encoder = encoders.NestedMultiPartEncoder()
        return encoder.encode(self.BOUNDARY, data)
