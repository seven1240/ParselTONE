import logging

# create a log target for this module
logger = logging.getLogger(__name__)


def requires_attr(name, default=False, evaluate=lambda value: value, 
        log_errors=True):
    """
    Decorator for a class method which will use getattr to find the value
    of the named attribute (using given default), then verify that the value 
    evaluates to True. If the log_errors keyword is False, errors will be raised, 
    instead of logged.
    
        >>> class Cat():
        ...     @requires_attr('claws', log_errors=False)
        ...     def climb(self):
        ...         print 'I am climbing a tree, and life is wonderful!'
        ...
        >>> cat = Cat()
        >>> cat.climb()
        Traceback (most recent call last):
            ...
        AttributeError: 'Cat.claws' missing or empty, but 'climb' requires it.
        >>> cat.claws = 'sharp'
        >>> cat.climb()
        I am climbing a tree, and life is wonderful!
    
    The error message when the attribute is missing can be customized by
    setting the _NAME_required_error attribute on the class to a string
    that accepts the formatting values object, attr, and func:

        >>> class Cat():
        ...     _claws_required_error = "{object} has no {attr}, cannot {func}!"
        ...     @requires_attr('claws', log_errors=False)
        ...     def climb(self):
        ...         print 'I am climbing a tree, and life is wonderful!'
        ...
        >>> cat = Cat()
        >>> cat.climb()
        Traceback (most recent call last):
            ...
        AttributeError: Cat has no claws, cannot climb!
    """
    def _decorated(func):
        def _do_func(self, *args, **kwargs):
            if not getattr(self, name, False):
                message = getattr(self, '_%s_required_error' % name, 
                    "'{object}.{attr}' missing or empty, but " \
                    "'{func}' requires it.").format(
                        attr=name, 
                        object=self.__class__.__name__,
                        func=func.__name__,
                    )
                if not log_errors:
                    raise AttributeError(message)
                logger.error(message)
                return None
            return func(self, *args, **kwargs)
        return _do_func
    return _decorated


if __name__ == "__main__":
    import doctest
    doctest.testmod()

