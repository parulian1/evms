from rest_framework import serializers

def get_entity_href_serializer(model_class, meta_extra_kwargs=None, *init_args, **init_kwargs):
    class EntityHrefSerializer(serializers.HyperlinkedModelSerializer):
        name = serializers.CharField(required=False)

        class Meta:
            model = model_class
            fields = ('href', 'name',)
            extra_kwargs = meta_extra_kwargs if meta_extra_kwargs is not None else {'href': {'lookup_field': 'slug', }, }

    return EntityHrefSerializer(*init_args, **init_kwargs)