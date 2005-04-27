"""
This modules provides the MinimalMatch class.  Subclasses from this
class have the special property that attribute names can be
abbreviated:

>>> class MyClass(MinimalMatch):
...     user = 'root'
...     start = 'yesterday'
...     stop = 'tomorrow'
... 
>>> my_instance = MyClass()

For instance the following command will set the 'user' attribute:

>>> my_instance.u = 'nobody'
>>> print my_instance.user
nobody

But of course you can always use the full attribute name:

>>> my_instance.user = 'root'
>>> print my_instance.us
root

Never type more than the full attribute name:

>>> print my_instance.users
Traceback (most recent call last):
  ...
AttributeError: MyClass instance has no attribute 'users'

Abbreviations should not be ambiguous:

>>> my_instance.st = 'now'
Traceback (most recent call last):
  ...
AttributeError: MyClass instance attribute 'st' is ambiguous

And setting instance attributes that are not class attributes is not
possible:

>>> my_instance.group = 'nobody'
Traceback (most recent call last):
  ...
AttributeError: MyClass instance has no attribute 'group'

>>> print my_instance.stop
tomorrow

"""

class MinimalMatch:
    """ Allow class attribute names to be abbreviated. """

    def _findattr(self, name):
        # Disregard private attributes.
        if name.startswith('_'):
            return (name, self.__dict__)

        match_attr = None
        match_dict = None
        if name in self.__dict__:
            match_attr = name
            match_dict = self.__dict__
        else:
            for dict in self.__dict__, self.__class__.__dict__:
                for attr in dict:
                    if attr.startswith(name):
                        if match_attr and attr != match_attr:
                            msg = "%s instance attribute '%s' is ambiguous" \
                                  % (self.__class__.__name__, name)
                            raise AttributeError, msg
                        else:
                            match_attr = attr
                            if not match_dict:
                                match_dict = dict

        if not match_attr:
            msg = "%s instance has no attribute '%s'" \
                  % (self.__class__.__name__, name)
            raise AttributeError, msg

        return (match_attr, match_dict)

    def __getattr__(self, name):
        (attr, dict) = self._findattr(name)
        return getattr(self, attr)

    def __setattr__(self, name, value):
	(attr, dict) = self._findattr(name)
	self.__dict__[attr] = value


# Tests.
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
