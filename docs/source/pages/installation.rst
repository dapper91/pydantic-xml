.. _installation:


Installation
~~~~~~~~~~~~

This part of the documentation covers the installation of ``pydantic-xml`` library.


Installation using pip
______________________

To install ``pydantic-xml``, run:

.. code-block:: console

    $ pip install pydantic-xml[lxml]

.. hint::

    ``pydantic-xml`` library supports `lxml <https://lxml.de/>`_ as an xml serializer backend.
    To use ``lxml`` instead of standard :py:mod:`xml.etree.ElementTree` parser install ``lxml`` extra.
