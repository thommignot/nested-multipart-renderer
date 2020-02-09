import tempfile

from django.conf.urls import url
from django.test import TestCase, override_settings

from PIL import Image
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


class NestedFilesSerializer(serializers.Serializer):
    name = fields.CharField()
    doc = fields.FileField()

    class Meta:
        fields = ('name', 'doc', 'deps')

    def get_fields(self):
        fields = super(NestedFilesSerializer, self).get_fields()
        fields['deps'] = NestedFilesSerializer(required=False, many=True)
        return fields


class NestedNameSerializer(serializers.Serializer):
    name = fields.CharField()

    class Meta:
        fields = ('name', 'deps')

    def get_fields(self):
        fields = super(NestedNameSerializer, self).get_fields()
        fields['deps'] = NestedNameSerializer(required=False, many=True)
        return fields


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


@api_view(['POST'])
def post_files_view(request):
    serializer = NestedFilesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    render_serializer = NestedNameSerializer(data=serializer.validated_data)
    render_serializer.is_valid(raise_exception=True)
    return Response(render_serializer.validated_data)


urlpatterns = [
    url(r'^post-complex-view/$', post_complex_view),
    url(r'^post-files-view/$', post_files_view)
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

    def test_nested_multipart_file(self):
        """
        NestedMultiPart is usefull to send nested files
        so this is what realy should work or we'd use
        a json format
        """
        args = ('RGB', (20, 20))
        images = list()
        for i in range(0, 5):
            image = Image.new(*args)
            image_file = tempfile.NamedTemporaryFile(suffix='.jpeg')
            image.save(image_file)
            image_file.seek(0)
            images.append(image_file)

        data = {
            'name': 'file_0_lvl_0.jpeg',
            'doc': images[0],
            'deps': [{
                'name': 'file_0_lvl_1.jpeg',
                'doc': images[1],
                'deps': [],
            }, {
                'name': 'file_1_lvl_1.jpeg',
                'doc': images[2],
                'deps': [{
                    'name': 'file_0_lvl_2.jpeg',
                    'doc': images[3]
                }, {
                    'name': 'file_1_lvl_2.jpeg',
                    'doc': images[4],
                    'deps': (),
                }]
            }]
        }
        response = self.client.post(
            path='/post-files-view/',
            data=data,
            format='nestedmultipart'
        )
        assert response.status_code == 200, response.data
        assert response.data == {
            'name': 'file_0_lvl_0.jpeg',
            'deps': [
                {'name': 'file_0_lvl_1.jpeg'},
                {
                    'name': 'file_1_lvl_1.jpeg',
                    'deps': [
                        {'name': 'file_0_lvl_2.jpeg'},
                        {'name': 'file_1_lvl_2.jpeg'}
                    ]
                }
            ]
        }
