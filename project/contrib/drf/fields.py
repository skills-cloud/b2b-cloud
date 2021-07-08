import enum

from rest_framework import fields


class EnumField(fields.ChoiceField):
    def __init__(
            self,
            choices=None,
            default=None,
            to_choice=lambda x: (x.value, x.name),
            to_repr=lambda x: x.name,
            **kwargs
    ):
        self.enum_class = choices
        self.to_repr = to_repr
        self.to_choice = to_choice
        kwargs['choices'] = [to_choice(e) for e in self.enum_class]
        if isinstance(default, enum.Enum):
            default = default.value
        kwargs['default'] = default
        kwargs.pop('max_length', None)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return self.enum_class(data)
        except (KeyError, ValueError):
            pass
        self.fail('invalid_choice', input=data)

    def to_representation(self, value):
        if not value:
            return None
        if isinstance(value, enum.Enum):
            return self.to_repr(value)
        else:
            return value
