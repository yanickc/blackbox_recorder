# Goal

Storage for arguments and values to be printed to log or
saved for future reference.

Automates gathering function arguments, local variables,
object properties and arbitrary key value pairs.

Keeps copies of values.

Use functions get_params_storage() and del_params_storage() to access
a Recorder instance globally without the need to share
the instance, in the same way is logging.getLogger().


# Examples

```python
from blackbox_recorder import get_recorder

storage = get_recorder("test")

class A:
    def f(self, a, *args, param1=11, param2=22, **kwargs):
        storage.store_args(self)

obj = A()
obj.f(1, 2, 3, param1=42, extra_param=123)
storage.print_to_log()                             
storage.clear()  
```
        
```
# Output:

Instance of class 'A' (<class 'params_logging.test_store_args.<locals>.A'>) (id:11004BDD0):
{
    "a": 1,
    "extra_param": 123,
    "param1": 42,
    "param2": 22,
    "varargs": [
        2,
        3
    ]
}
```