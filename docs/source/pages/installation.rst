.. _installation:


Installation
~~~~~~~~~~~~

This part of the documentation covers the installation of ``pydantic-xml`` library.


Installation using pip
______________________

To install ``pydantic-xml``, run:

.. code-block:: console

    $ pip install pydantic-xml


Optional dependencies
_____________________

``pydantic-xml`` library supports `lxml <https://lxml.de/>`_ as an xml serialization backend.
If you wish to use ``lxml`` instead of standard :py:mod:`xml.etree.ElementTree` parser install ``lxml`` extra:

.. code-block:: console

    $ pip install pydantic-xml[lxml]
