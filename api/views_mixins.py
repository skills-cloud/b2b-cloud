class ViewSetFilteredByUserMixin:
    def get_queryset(self):
        return super().get_queryset().filter_by_user(self.request.user)
