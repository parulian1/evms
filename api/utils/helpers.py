from http import HTTPStatus

from rest_framework import exceptions, serializers
from rest_framework.views import Response, exception_handler

def get_entity_href_serializer(model_class, meta_extra_kwargs=None, *init_args, **init_kwargs):
    class EntityHrefSerializer(serializers.HyperlinkedModelSerializer):
        name = serializers.CharField(required=False)

        class Meta:
            model = model_class
            fields = ('href', 'name',)
            extra_kwargs = meta_extra_kwargs if meta_extra_kwargs is not None else {'href': {'lookup_field': 'slug', }, }

    return EntityHrefSerializer(*init_args, **init_kwargs)


def api_exception_handler(exception: Exception, context: dict) -> Response:
    """Custom API exception handler."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exception, context)

    # Only alter the response when it's a validation error
    if not isinstance(exception, exceptions.ValidationError):
        return response

    # It's a validation error, there should be a Serializer
    view = context.get("view", None)
    serializer = view.get_serializer_class()()

    field_errors = {}
    main_error = ""
    for key, details in response.data.items():

        if key != "non_field_errors":
            if key in serializer.fields:
                label = serializer.fields[key].label

                for message in details:
                    field_errors[label.lower()] =  f'{message}'
            else:
                for message in details:
                    field_errors[key.lower()] =  f'{message}'
        else:
            main_error = ','.join(details)

    # Using the description's of the HTTPStatus class as error message.
    http_code_to_message = {v.value: v.description for v in HTTPStatus}

    error_payload = {
        "status_code": response.status_code,
        "type": "ValidationError",
        "message": http_code_to_message[response.status_code],
        "details": {
            "field_errors": field_errors,
            "main_error": main_error
        },

    }

    # Overwrite default exception_handler response data
    response.data = error_payload

    return response
