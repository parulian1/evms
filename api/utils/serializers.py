from rest_framework import serializers


class TokenInvalidSerializer(serializers.Serializer):
    token_class = serializers.CharField()
    token_type = serializers.CharField()
    message = serializers.CharField()

class UnauthorizedSerializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField()
    messages = TokenInvalidSerializer(many=True)