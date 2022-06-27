##
# @file
# @author Hendrik Boeck <hendrikboeck.dev@protonmail.com>
#
# @package   Paperwrite.PyAdditions.Types
# @namespace Paperwrite.PyAdditions.Types
#
# Package containing extra general types and patterns not included in STL for
# Python. Adds GoF pattern singleton.

# -- FUTURE (subject to change, handle with care)
#from __future__ import annotations

# -- STL
from typing import Any, Dict, TypeVar, Type
import warnings

##
# Alias for template type T
T = TypeVar("T")


##
# @brief GoF pattern singleton
#
# Metaclass defining the GoF pattern singleton. You can call the constructor
# once explicit with `Init()`, after the initialization the `Init()` function
# will behave like `Instance()`. If you want to reinitialize the object you can
# call the `ForceInit()` function, which will create a new object in place. If
# you try to call `__call__()` it will result in a TypeError.
#
# @see
#  - Singleton
class SingletonMeta(type):

  __instances__: Dict[type, Any] = {}

  ##
  # Type Constructor
  #
  # @param  *args   variable length argument list
  # @param  **kwargs  arbitrary keyword arguments
  #
  # @throws TypeError
  def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> Any:
    raise TypeError(
        f"{cls.__module__}.{cls.__qualname__} has no public constructor")

  ##
  # Deletes the singleton.
  def Delete(cls: Type[T]) -> None:
    if cls.__instances__.get(cls) is not None:
      del cls.__instances__[cls]

  ##
  # Reinitializes the singleton in place.
  #
  # @warning will overwrite current singleton instance
  def ForceInit(cls: Type[T], *args: Any, **kwargs: Any) -> T:
    cls.Delete()
    return cls.Init(*args, **kwargs)

  ##
  # Returns the singleton instance. Upon its first call, it creates a new
  # instance of the decorated class and calls its `__init__` method with
  # specified arguments. On all subsequent calls, the already created instance
  # is returned.
  #
  # @param  *args   variable length argument list
  # @param  **kwargs  arbitrary keyword arguments
  #
  # @return singleton instance
  def Init(cls: Type[T], *args: Any, **kwargs: Any) -> T:
    if cls.__instances__.get(cls) is not None:
      warnings.warn(
          "Object already has been initialized at an earlier time. Handeled "
          "init() as instance().", RuntimeWarning)
    else:
      cls.__instances__[cls] = super(SingletonMeta,
                                     cls).__call__(*args, **kwargs)
    return cls.__instances__[cls]

  ##
  # Returns the singleton instance. Upon its first call, it creates a new
  # instance of the decorated class and calls its `__init__` method without any
  # arguments. On all subsequent calls, the already created instance is
  # returned.
  #
  # @return singleton instance
  def Instance(cls: Type[T]) -> T:
    if cls.__instances__.get(cls) is not None:
      return cls.__instances__.get(cls)
    else:
      return cls.Init()


##
# A non-thread-safe helper class to ease implementing singletons. Wrapper for
# SingletonMeta class.
#
# @see
#  - SingletonMeta
class Singleton(metaclass=SingletonMeta):
  pass
