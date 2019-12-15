import pytest

from params_record import get_params_storage, del_params_storage


def test_store_args():
    storage = get_params_storage("test")

    class A:
        def f(self, a, *args, param1=11, param2=22, **kwargs):
            storage.store_args(self)

    obj = A()
    obj.f(1, 2, 3, param1=42, extra_param=123)
    storage.print_to_log()

    assert storage[obj]["a"] == 1
    assert storage[obj]["extra_param"] == 123
    assert storage[obj]["param1"] == 42
    assert storage[obj]["param2"] == 22
    assert storage[obj]["varargs"][0] == 2
    assert storage[obj]["varargs"][1] == 3

    del_params_storage("test")


def test_store_locals():
    storage = get_params_storage("test")

    def my_func():
        my_local = 41
        my_local += 1

        storage.store_locals("my_func", ["my_local"])
        storage.print_to_log()

    my_func()

    assert storage["my_func"]["my_local"] == 42

    del_params_storage("test")


def test_store_locals_with_error():
    storage = get_params_storage("test")

    def my_func():
        my_local = 41
        my_local += 1

        storage.store_locals("my_func", ["my_local", "xxxx"])
        storage.print_to_log()

    with pytest.raises(KeyError):
        my_func()

    del_params_storage("test")


def test_store_properties():
    storage = get_params_storage("test")

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

    del_params_storage("test")


def test_store_settings():
    storage = get_params_storage("test")

    storage.store_settings("my_key", {"a": 1, "b": 2, "c": 3})
    storage.print_to_log()

    assert storage["my_key"]["a"] == 1
    assert storage["my_key"]["b"] == 2
    assert storage["my_key"]["c"] == 3

    del_params_storage("test")
