from django.db.models import F
from django_filters import MultipleChoiceFilter, ModelMultipleChoiceFilter
from django_filters.widgets import CSVWidget, DateRangeWidget as DateRangeWidgetBase
from rest_framework.filters import OrderingFilter


class OrderingFilterNullsLast(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset


class OrderingFilterNullsFirst(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=False))
                else:
                    f_ordering.append(F(o).asc(nulls_last=False))

            return queryset.order_by(*f_ordering)

        return queryset


class CSVWidgetFilterMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(widget=CSVWidget, *args, **kwargs)


class MultipleChoiceCommaSeparatedFilter(CSVWidgetFilterMixin, MultipleChoiceFilter):
    pass


class ModelMultipleChoiceCommaSeparatedFilter(CSVWidgetFilterMixin, ModelMultipleChoiceFilter):
    pass


class ModelMultipleChoiceCommaSeparatedIdFilter(CSVWidgetFilterMixin, ModelMultipleChoiceFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        return super().filter(qs, [o.id if not isinstance(o, int) else o for o in value])


class DateRangeWidget(DateRangeWidgetBase):
    suffixes = ['from', 'to']
