import inspect


def is_call_from_admin() -> bool:
    return '/admin.py' in '\n'.join([x.filename for x in inspect.stack()])
