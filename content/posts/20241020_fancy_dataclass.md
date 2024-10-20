Title: New Python Library: <i>fancy_dataclass</i>
Category: Python
Tags: Python
Summary: Introducing `fancy_dataclass`, a versatile Python library built around dataclasses.

I've written a Python library called `fancy_dataclass`, a versatile Python library built around dataclasses. Python 3.7 introduced the [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module, which lets you write "statically typed" classes using the type hinting mechanism.

The goal of this library is to enable *type-driven development*, which leverages the type system to eliminate a lot of boilerplate code. The idea is that you write a dataclass and then imbue with with "special powers." One common use case is to enable automatic conversion of Python objects to and from JSON. Another is to define a bundle of parameters and then expose them to a command-line argument parser. `fancy_dataclass` makes it possible to do these things with very few lines of code.

I am eager to have people try using it and provide feedback, so please check it out!

To install the library, do: `pip install fancy_dataclass`

It should support Python versions 3.8–3.12.

📝 Read the documentation [here](https://fancy-dataclass.readthedocs.io/en/latest/).

🪲 Submit bug reports or feature requests on [Github](https://github.com/jeremander/fancy-dataclass).

### Example 1: JSON Serialization

Let's define a dataclass that can be converted to and from JSON.

```python
from dataclasses import dataclass
from fancy_dataclass import JSONDataclass

@dataclass
class Person(JSONDataclass):
    name: str
    age: int
    height: float
    hobbies: list[str]
```

Then we can easily convert a `Person` to a Python dictionary or a JSON string.

```python
# create a Person
>>> person = Person(
    name='John Doe',
    age=47,
    height=71.5,
    hobbies=['reading', 'juggling', 'cycling']
)

# convert to Python dict
>>> person.to_dict()
{'name': 'John Doe',
 'age': 47,
 'height': 71.5,
 'hobbies': ['reading', 'juggling', 'cycling']}

# convert to JSON string
>>> print(person.to_json_string(indent=2))

{
  "name": "John Doe",
  "age": 47,
  "height": 71.5,
  "hobbies": [
    "reading",
    "juggling",
    "cycling"
  ]
}
```

It's easy to convert in the other direction, too:

```python
>>> person = Person.from_json_string('{"name": "John Doe", "age": 47, "height": 71.5, "hobbies": ["reading", "juggling", "cycling"]}')
>>> person
Person(name='John Doe', age=47, height=71.5, hobbies=['reading', 'juggling', 'cycling'])
```

`fancy_dataclass` supports serialization of [TOML](https://toml.io/en/) as well as JSON, which is useful for configuration management.

### Example 2: CLI Argument Parsing

Let's use `fancy_dataclass` to write a simple command-line program, `greet.py`:

```python
from dataclasses import dataclass, field

from fancy_dataclass import CLIDataclass

@dataclass
class Greet(CLIDataclass):
    """A program to greet the user."""
    name: str = field(
        metadata={
            'help': 'name of person to greet'
        }
    )
    num_exclamations: int = field(
        default=1,
        metadata={
            'args': ['-n', '--num-exclamations'],
            'help': 'number of exclamation points'
        }
    )
    fancy: bool = field(
        default=False,
        metadata={
            'help': 'greet fancily'
        }
    )

    def run(self) -> None:
        # implement your main program logic
        if self.fancy:
            greeting = 'Greetings and salutations'
        else:
            greeting = 'Hello'
        exclamations = '!' * self.num_exclamations
        print(f'{greeting}, {self.name}{exclamations}')


if __name__ == '__main__':
    Greet.main()
```

This will create a full-fledged command-line program with argument parsing, without having to write any of it manually. You can view the help menu with:

```text
python greet.py --help
```

Which prints out:

```text
usage: greet.py [-h] [-n NUM_EXCLAMATIONS] [--fancy] name

A program to greet the user.

positional arguments:
  name                  name of person to greet

options:
  -h, --help            show this help message and exit
  -n NUM_EXCLAMATIONS, --num-exclamations NUM_EXCLAMATIONS
                        number of exclamation points
  --fancy               greet fancily
```

Note that `fancy_dataclass` uses the dataclass field metadata to construct the appropriate argument names and help strings for this menu.

Let's try running the program with a few different arguments:

```text
$ python greet.py Bob
Hello, Bob!

$ python greet.py Alice --fancy
Greetings and salutations, Alice!

$ python greet.py Alice --fancy -n 3
Greetings and salutations, Alice!!!

$ python greet.py
usage: greet.py [-h] [-n NUM_EXCLAMATIONS] [--fancy] name
greet.py: error: the following arguments are required: name
```

We see that dataclass fields with a default value are optional, while those without a default are required.

### Other Features

In addition to the examples above, `fancy_dataclass` can do much more, including:

*Configuration management*: store global configurations and use them anywhere in your program
*SQL persistence*: define SQL tables, and save/load objects from a database
*Subprocess calls*: generate command-line arguments to be passed to another program

You are free to combine the features together so that the same dataclass can be used for multiple purposes (e.g. both SQL and JSON representation).

There is also a system for adjusting class-specific or field-specific settings (e.g. for JSON serialization, whether to suppress `None` values or default values); see the documentation for details.

### What about `pydantic`?

Some of the features in this library, like JSON serialization, are also available in the popular [pydantic](https://docs.pydantic.dev/latest/) library. `pydantic` also provides field *validation*, which `fancy_dataclass` does not (yet) do, and a host of other features. On the other hand, `fancy_dataclass` has features that `pydantic` does not have, like command-line parsing.

While `fancy_dataclass` does overlap with `pydantic` in some ways, it was designed to be as lightweight as possible, both in terms of dependencies and configurations. Another main difference is that `pydantic` classes must inherit from `BaseModel` (or use a special `pydantic.dataclasses.dataclass` decorator), while `fancy_dataclass` uses the ordinary `dataclass` decorator with additional "mixin" classes like `JSONDataclass`, `CLIDataclass`, etc. depending on what features you want to use.

You can also use both `fancy_dataclass` and `pydantic` together to get the best of both worlds.

### Conclusion

Anyway, I hope you enjoy using this library, and I am always happy to respond to any bug reports and feature requests! Feel free to follow the project on [Github](https://github.com/jeremander/fancy-dataclass) or e-mail me at <jeremys@nessiness.com>.
