"""
Storage for arguments and values to be printed to log or
saved for future reference.

Automates gathering function arguments, local variables,
object properties and arbitrary key value pairs.

Keeps copies of values.

Use functions get_recorder() and del_recorder() to access
a Recorder instance globally without the need to share
the instance, in the same way as logging.getLogger().
"""

import inspect
import logging
from collections import defaultdict
from copy import deepcopy
from pprint import pformat
from typing import Dict, Iterable, Union

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Recorder(defaultdict):
    def __init__(self) -> None:
        super().__init__(dict)

    def store_args(self, key: Union[str, object]) -> None:
        """
        Store arguments names and values of the calling function.

        ```
        class A:
            def f(self, a, *args, param1=11, param2=22, **kwargs):
                storage.store_args(self)

        obj = A()
        obj.f(1, 2, 3, param1=42, extra_param=123)
        storage.print_to_log()
        ```

        # Output:

        ====== Instance 'A' (<class 'params_record_tests.test_store_args.<locals>.A'>) (id:10B81F310) ======

        {'a': 1, 'extra_param': 123, 'param1': 42, 'param2': 22, 'varargs': (2, 3)}
        """
        v = self[key]
        frame = inspect.currentframe().f_back
        arg_values = inspect.getargvalues(frame)

        for a in arg_values.args:
            if a != "self":
                v[a] = deepcopy(arg_values.locals[a])

        varargs = arg_values.varargs
        if arg_values.varargs is not None:
            varargs = arg_values.locals[varargs]
            if len(varargs) > 0:
                v["varargs"] = deepcopy(varargs)

        keywords = arg_values.keywords
        if arg_values.varargs is not None:
            v.update(deepcopy(arg_values.locals[keywords]))

    def store_locals(
        self, key: Union[str, object], variable_names: Iterable[str]
    ) -> None:
        """
        Store the local variables names and values of the calling function.

        ```
        def my_func():
            my_local = 41
            my_local += 1

            storage.store_locals("my_func", ["my_local"])
            storage.print_to_log()

        my_func()
        ```

        # Output:

        ============================================ 'my_func' =============================================

        {'my_local': 42}

        """
        v = self[key]
        frame = inspect.currentframe().f_back
        arg_values = inspect.getargvalues(frame)

        for n in variable_names:
            if n in arg_values.locals:
                v[n] = deepcopy(arg_values.locals[n])
            else:
                raise KeyError(f"Variable '{n}' not found in locals variables.")

    def store_properties(
        self, key: Union[str, object], obj, property_names: Iterable[str]
    ) -> None:
        """
        Store the given properties names and values from the given object. Ex:

        ```
        class A:
            def __init__(self) -> None:
                super().__init__()

                self.a = 1
                self.b = 2
                self.c = 3

        a = A()
        storage.store_properties("my_key", a, ["a", "c"])
        storage.print_to_log()
        ```

        # Output:

        ============================================= 'my_key' =============================================

        {'a': 1, 'c': 3}
        """
        v = self[key]

        for p in property_names:
            if p in obj.__dict__:
                v[p] = deepcopy(obj.__dict__[p])
            else:
                raise KeyError(f"Property '{p}' not found in object '{obj}'.")

    def store_settings(self, key: Union[str, object], arg: Dict) -> None:
        """
        Store arbitrary key balues paris under the given key.

        ```
        storage.store_settings("my_key", {"a": 1, "b": 2, "c": 3})
        storage.print_to_log()
        ```

        # Output:

        ============================================= 'my_key' =============================================

        {'a': 1, 'b': 2, 'c': 3}
        """

        self[key].update(deepcopy(arg))

    def format(self) -> str:
        """
        Return formatted string with the current stored values.

        Ex.:

        ====== Instance 'A' (<class 'params_record_tests.test_store_args.<locals>.A'>) (id:10B81F310) ======

        {'a': 1, 'extra_param': 123, 'param1': 42, 'param2': 22, 'varargs': (2, 3)}

        """

        lines = ["\n"]

        for k, v in super().items():
            if isinstance(k, str):
                title = f" '{k}' "
            else:
                title = f" Instance '{k.__class__.__name__}' ({k.__class__}) (id:{id(k):X}) "

            obj_description = f"{title:=^100}\n"
            lines.append(obj_description)
            lines.append(pformat(v, width=120, compact=True))
            lines.append("")

        return "\n".join(lines)

    def print_to_log(self) -> None:
        """
        Print the current stored values to log.

        Ex.:

        ====== Instance 'A' (<class 'params_record_tests.test_store_args.<locals>.A'>) (id:10B81F310) ======

        {'a': 1, 'extra_param': 123, 'param1': 42, 'param2': 22, 'varargs': (2, 3)}

        """

        logger.info(self.format())

    def clear(self):
        """
        Remove all items.
        """
        super().clear()
