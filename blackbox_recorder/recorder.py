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

        :param key: Key under which to store the values. In case of an object, its class name and id will be used.
        :return: None


        ```
        class A:
            def f(self, a, *args, param1=11, param2=22, **kwargs):
                storage.store_args(self)

        obj = A()
        obj.f(1, 2, 3, param1=42, extra_param=123)
        storage.print_to_log()
        ```

        # Output:

        ========= A (<class 'blackbox_recorder_tests.test_store_args.<locals>.A'>) (id:112CEA390) ==========

        {'a': 1, 'extra_param': 123, 'param1': 42, 'param2': 22, 'varargs': (2, 3)}

        """
        key = self._make_key(key)

        v = self[key]
        frame = inspect.currentframe().f_back
        arg_values = inspect.getargvalues(frame)

        for a in arg_values.args:
            if a != "self":
                v[a] = self._grab(arg_values.locals[a])

        varargs = arg_values.varargs
        if arg_values.varargs is not None:
            varargs = arg_values.locals[varargs]
            if len(varargs) > 0:
                v["varargs"] = self._grab(varargs)

        keywords = arg_values.keywords
        if arg_values.varargs is not None:
            v.update(self._grab(arg_values.locals[keywords]))

    def store_locals(self, key: Union[str, object], variable_names: Iterable[str]) -> None:
        """
        Store the local variables names and values of the calling function.

        :param key: Key under which to store the values. In case of an object, its class name and id will be used.
        :param variable_names: Names of local variables to store the values of.
        :return: None

        ```
        def my_func():
            my_local = 41
            my_local += 1

            storage.store_locals("my_func", ["my_local"])
            storage.print_to_log()

        my_func()
        ```

        # Output:

        ============================================= my_func ==============================================

        {'my_local': 42}

        """
        key = self._make_key(key)

        v = self[key]
        frame = inspect.currentframe().f_back
        arg_values = inspect.getargvalues(frame)

        for n in variable_names:
            if n in arg_values.locals:
                v[n] = self._grab(arg_values.locals[n])
            else:
                raise KeyError(f"Variable '{n}' not found in locals variables.")

    def store_properties(self, key: Union[str, object], obj, property_names: Iterable[str]) -> None:
        """
        Store the given properties names and values from the given object. Ex:

        :param key: Key under which to store the values. In case of an object, its class name and id will be used.
        :param obj: Object from which to store values.
        :param property_names: Names of object properties to store the values of.
        :return: None

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

        ============================================== my_key ==============================================

        {'a': 1, 'c': 3}

        """
        key = self._make_key(key)

        v = self[key]

        for p in property_names:
            if p in obj.__dict__:
                v[p] = self._grab(obj.__dict__[p])
            else:
                raise KeyError(f"Property '{p}' not found in object '{obj}'.")

    def store_values(self, key: Union[str, object], arg: Dict) -> None:
        """
        Store arbitrary key balues paris under the given key.

        :param key: Key under which to store the values. In case of an object, its class name and id will be used.
        :param arg: Dict with names and values to store.
        :return: None

        ```
        storage.store_values("my_key", {"a": 1, "b": 2, "c": 3})
        storage.print_to_log()
        ```

        # Output:

        ============================================== my_key ==============================================

        {'a': 1, 'b': 2, 'c': 3}

        """

        self[key].update(self._grab(arg))

    def format(self, header="", compact=True) -> str:
        """
        Return formatted string with the current stored values.

        :param header:  Header message.
        :type compact:  If compact is false each item of a long sequence will be formatted on a separate line.
                        If compact is true, as many items as will fit within the width will be formatted
                        on each output line.

        Ex.:

        ====== Instance 'A' (<class 'params_record_tests.test_store_args.<locals>.A'>) (id:10B81F310) ======

        {'a': 1, 'extra_param': 123, 'param1': 42, 'param2': 22, 'varargs': (2, 3)}

        """
        lines = [
            "",
            f"{header:=^140}",
        ]

        for k, v in super().items():
            lines.append("")
            lines.append(f"{' ' + k + ' ':-^140}")
            lines.append(pformat(v, width=120, compact=compact))

        lines.append("")
        lines.append("=" * 140)

        return "\n".join(lines)

    def print_to_log(self, header="", compact=True) -> None:
        """
        Print the current stored values to log.

        :type compact:  If compact is false each item of a long sequence will be formatted on a separate line.
                        If compact is true, as many items as will fit within the width will be formatted
                        on each output line.

        Ex.:

        ====== Instance 'A' (<class 'params_record_tests.test_store_args.<locals>.A'>) (id:10B81F310) ======

        {'a': 1, 'extra_param': 123, 'param1': 42, 'param2': 22, 'varargs': (2, 3)}

        """

        logger.info(self.format(header=header, compact=compact))

    def clear(self):
        """
        Remove all items.
        """
        super().clear()

    @staticmethod
    def _make_key(key: Union[str, object]) -> str:
        """
        Create a string key from objects class name and id.

        :param key: Key
        :return: String representation for the key.
        """
        if not isinstance(key, str):
            return f"{key.__class__.__name__} {key.__class__} object at 0x{id(key):x}"
        else:
            return key

    @staticmethod
    def _grab(value):
        if isinstance(value, (dict, list, tuple)):
            return deepcopy(value)
        elif isinstance(value, (bool, int, float, complex, str)):
            return value
        else:
            return value.__repr__()


recorders = defaultdict(Recorder)


def get_recorder(name: str) -> Recorder:
    return recorders[name]


def del_recorder(name: str) -> None:
    del recorders[name]
