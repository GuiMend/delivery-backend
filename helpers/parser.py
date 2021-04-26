import json

import six
from django.http import QueryDict
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import parsers, status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response


class MultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context
        )
        data = {}
        # find the data field and parse it
        try:
            data = json.loads(result.data["data"])
        except MultiValueDictKeyError as exc:

            data = result.data
        except json.decoder.JSONDecodeError as exc:
            raise ParseError('Multipart form parse error - %s' % six.text_type(exc))

        qdict = QueryDict('', mutable=True)
        qdict.update(data)
        return parsers.DataAndFiles(qdict, result.files)


def multipart_json_custom_create(self, request, *args, **kwargs):
    if isinstance(request.data, QueryDict):
        data = request.data.dict()
    else:
        data = request.data
    serializer = self.get_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)

    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def multipart_json_custom_update(self, request, *args, **kwargs):
    if isinstance(request.data, QueryDict):
        data = request.data.dict()
    else:
        data = request.data
    partial = kwargs.pop('partial', False)
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)

    if getattr(instance, '_prefetched_objects_cache', None):
        # If 'prefetch_related' has been applied to a queryset, we need to
        # forcibly invalidate the prefetch cache on the instance.
        instance._prefetched_objects_cache = {}

    return Response(serializer.data)
