"""
This module provides the Task class.  It extends the MinimalMatch
class from the MinimalMatch module with type and range checking on its
attributes:

>>> class MyTask(Task):
...     indisk = 0
...     infile = ''
...     pixavg = 1.0
...     aparms = 10*[0.0]
...     def __init__(self):
...         Task.__init__(self)
...         self._min_dict = {'indisk': 0, 'aparms': 0}
...         self._max_dict = {'indisk': 4, 'aparms': 10}
...         self._strlen_dict = {'infile': 14}
...
>>> my_task = MyTask()

It still has the property that attribute names can be abbreviated:

>>> print my_task.ind
0
>>> my_task.ind = 1
>>> print my_task.ind
1

But an exception will be thrown if you try to assign a value that is
out of range:

>>> my_task.ind = 5
Traceback (most recent call last):
  ...
ValueError: value '5' is out of range for attribute 'indisk'

Or if you try to assign a value that has the wrong type, such
assigning a string to an integer attribute:

>>> my_task.ind = 'now'
Traceback (most recent call last):
  ...
TypeError: value 'now' has invalid type for attribute 'indisk'

Assigning strings to string attributes works fine of course:

>>> my_task.infile = 'short'

As long as there is no limit on the length of a string:

>>> my_task.infile = 'tremendouslylong'
Traceback (most recent call last):
  ...
ValueError: string 'tremendouslylong' is too long for attribute 'infile'

Assigning an integer value to a floating point attribute is perfectly
fine of course:

>>> my_task.pixavg = 2
>>> print my_task.pixavg
2.0

The same should happen for lists:

>>> my_task.aparms = 10*[1]
>>> print my_task.aparms
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

For subscripting:

>>> my_task.aparms[0] = 0
>>> print my_task.aparms
[0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

And slice assignment:

>>> my_task.aparms[1:3] = [1, 2]
>>> print my_task.aparms
[0.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

You're not allowed to change the length of the list through slice
assignment though:

>>> my_task.aparms[3:6] = [3, 4, 5, 6]
Traceback (most recent call last):
  ...
TypeError: slice '3:6' changes the array size of attribute 'aparms'

"""

from MinimalMatch import MinimalMatch

class List(list):
    def __init__(self, task, attr, value):
        self._task = task
        self._attr = attr
        list.extend(self, value)

    def __setitem__(self, key, item):
        item = self._task._validateattr(self._attr, item, self[key])
        list.__setitem__(self, key, item)

    def __setslice__(self, low, high, seq):
        if not high - low == len(seq):
            msg = "slice '%d:%d' changes the array size of" \
                  " attribute '%s'" % (low, high, self._attr)
            raise TypeError, msg
        for key in xrange(low, high):
            self[key] = seq[key - low]


class Task(MinimalMatch):
    def __init__(self):
        self._min_dict = {}
        self._max_dict = {}
        self._strlen_dict = {}

    def _validateattr(self, attr, value, default):
        """Check whether VALUE is a valid valid for attribute ATTR."""

        # Do not check private attributes.
        if attr.startswith('_'):
            return value

        # Handle lists recursively.
        if isinstance(value, list) and isinstance(default, list):
            if len(value) != len(default):
                msg = "value '%s' does not match array size of" \
                      " attribute '%s'" % (value, attr)
                raise TypeError, msg
            for key in xrange(len(value)):
                value[key] = self._validateattr(attr, value[key], default[key])
            return List(self, attr, value)

        # Convert integers into floating point numbers if necessary.
        if type(value) == int and type(default) == float:
            value = float(value)

        # Check attribute type.
        if type(value) != type(default):
            msg = "value '%s' has invalid type for attribute '%s'" \
                  % (value, attr)
            raise TypeError, msg

        # Check range.
        if attr in self._min_dict:
            min = self._min_dict[attr]
            if not min <= value:
                msg = "value '%s' is out of range for attribute '%s'" \
                      % (value, attr)
                raise ValueError, msg
        if attr in self._max_dict:
            max = self._max_dict[attr]
            if not value <= max:
                msg = "value '%s' is out of range for attribute '%s'" \
                      % (value, attr)
                raise ValueError, msg

        # Check string length.
        if attr in self._strlen_dict:
            if len(value) > self._strlen_dict[attr]:
                msg = "string '%s' is too long for attribute '%s'" \
                      % (value, attr)
                raise ValueError, msg

        return value

    def __setattr__(self, name, value):
        (attr, dict) = self._findattr(name)

        if attr in dict:
            # Validate based on the value already present.
            value = self._validateattr(attr, value, dict[attr])

        self.__dict__[attr] = value


# Tests.
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
