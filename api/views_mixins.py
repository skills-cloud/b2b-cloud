from rest_framework.permissions import SAFE_METHODS


class ViewSetFilteredByUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter_by_user(self.request.user)


class ReadWriteSerializersMixin:
    serializer_class = None
    serializer_read_class = None

    def get_serializer_class(self):
        if not self.serializer_class and not self.serializer_read_class:
            raise RuntimeError(
                '- Are serializer_class or serializer_read_class defined?'
                '- NO'
            )
        if not self.serializer_read_class:
            return self.serializer_class
        if not self.serializer_class:
            return self.serializer_read_class
        if self.request.method in SAFE_METHODS:
            return self.serializer_read_class
        return self.serializer_class
