from django.conf.urls import url
from django.test import TestCase, override_settings

from rest_framework import fields, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.test import APIClient


class BasicSerializer(serializers.Serializer):
    flag = fields.BooleanField(default=lambda: True)


class IntermediateSerializer(serializers.Serializer):
    base = BasicSerializer(many=True)


class NestedSerializer(serializers.Serializer):
    dictionary = IntermediateSerializer()


class ComplexSerializer(serializers.Serializer):
    foo = NestedSerializer()
    bar = fields.IntegerField()
    baz = fields.IntegerField()


@api_view(['POST'])
def post_view(request):
    serializer = BasicSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data)


@api_view(['POST'])
def post_complex_view(request):
    serializer = ComplexSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data)


urlpatterns = [
    url(r'^post-complex-view/$', post_complex_view)
]


@override_settings(ROOT_URLCONF='tests.test_testing')
class TestAPITestClient(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_nested_multipart_data(self):
        """
        NestedMultiPart encoding supports nested data
        so it shouldn't raise if the user attempts to do so
        it should encode data so that nested serializers
        can parse it
        """
        data = {
            'baz': 42,
            'bar': 24,
            'foo': {
                'dictionary': {
                    'base': [
                        {'flag': True},
                        {'flag': False}
                    ]
                }
            }
        }
        response = self.client.post(
            path='/post-complex-view/',
            data=data,
            format='nestedmultipart'
        )
        assert response.status_code == 200
        assert response.data == data
