.. _KludgeIntro:

Introduction
=============

Kludge is a tool that makes it easier to wrap C++ libraries into KL extensions.

Kludge roughly consists of three parts:

- An *API description language* that decribes a C++ API in a way that Kludge can use to generate an extension that wraps the API.  This description language is a set of objets and methods in Python; files written in this language are Python scripts, and by convention have the suffix ``.kludge.py``.  This decription language is similar in concept to the DSL used by `boost.python <http://www.boost.org/doc/libs/1_62_0/libs/python/doc/html/index.html>`_.  A simple example in this language could be:

  .. code-block:: python

    ext.add_func('AddTwoInts', 'int', ['int', 'int'])

- A *generate* tool that takes an API description written in this language and generates a KL extension, written in both C++ and KL, that wraps the API.

- A *discover* tool that takes C++ header files and tries to generate an API description in the description language.  It is impossible to map every possible C++ API to the API description language but the discover tool tries hard and can wrap many common cases.

It is because it is impossible to automatically map every possible C++ API to KL automatically that the description language exists.  There are many different ways that the API can be too complex to automatically map into KL; for instance, KL does not support templates, and therefore if we wish to use templated C++ codes within KL we must instantiate the templates using the types we wish to use it with.
