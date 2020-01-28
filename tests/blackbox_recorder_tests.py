import logging
import pytest

logging.basicConfig(level=logging.DEBUG)

from blackbox_recorder.recorder import get_recorder, del_recorder


def test_store_args():
    storage = get_recorder("test")

    class A:
        def f(self, a, *args, param1=11, param2=22, **kwargs):
            storage.store_args(self)

    obj = A()
    obj.f(1, 2, 3, param1=42, extra_param=123)
    storage.print_to_log()

    key = storage._make_key(obj)

    assert storage[key]["a"] == 1
    assert storage[key]["extra_param"] == 123
    assert storage[key]["param1"] == 42
    assert storage[key]["param2"] == 22
    assert storage[key]["varargs"][0] == 2
    assert storage[key]["varargs"][1] == 3

    del_recorder("test")


def test_store_locals():
    storage = get_recorder("test")

    def my_func():
        my_local = 41
        my_local += 1

        storage.store_locals("my_func", ["my_local"])
        storage.print_to_log()

    my_func()

    assert storage["my_func"]["my_local"] == 42

    del_recorder("test")


def test_store_locals_with_error():
    storage = get_recorder("test")

    def my_func():
        my_local = 41
        my_local += 1

        storage.store_locals("my_func", ["my_local", "xxxx"])
        storage.print_to_log()

    with pytest.raises(KeyError):
        my_func()

    del_recorder("test")


def test_store_properties_with_property_list():
    storage = get_recorder("test")

    class A:
        def __init__(self) -> None:
            super().__init__()

            self.a = 1
            self.b = 2
            self.c = 3

    a = A()

    storage.store_properties("my_key", a, ["a", "c"])
    storage.print_to_log()

    assert storage["my_key"]["a"] == 1
    assert "b" not in storage["my_key"]
    assert storage["my_key"]["c"] == 3

    del_recorder("test")


def test_store_properties_without_property_list():
    storage = get_recorder("test")

    class A:
        def __init__(self) -> None:
            super().__init__()

            self.a = 1
            self.b = 2
            self.c = 3

    a = A()

    storage.store_properties("my_key", a)
    storage.print_to_log()

    assert storage["my_key"]["a"] == 1
    assert storage["my_key"]["b"] == 2
    assert storage["my_key"]["c"] == 3
    assert len(storage["my_key"]) == 3

    del_recorder("test")


def test_store_settings():
    storage = get_recorder("test")

    storage.store_values("my_key", {"a": 1, "b": 2, "c": 3})
    storage.print_to_log()

    assert storage["my_key"]["a"] == 1
    assert storage["my_key"]["b"] == 2
    assert storage["my_key"]["c"] == 3

    del_recorder("test")
