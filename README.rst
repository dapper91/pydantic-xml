
pydantic-xml extension
======================

.. image:: https://static.pepy.tech/personalized-badge/pydantic-xml?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads/month
    :target: https://pepy.tech/project/pydantic-xml
    :alt: Downloads/month
.. image:: https://github.com/dapper91/pydantic-xml/actions/workflows/test.yml/badge.svg?branch=master
    :target: https://github.com/dapper91/pydantic-xml/actions/workflows/test.yml
    :alt: Build status
.. image:: https://img.shields.io/pypi/l/pydantic-xml.svg
    :target: https://pypi.org/project/pydantic-xml
    :alt: License
.. image:: https://img.shields.io/pypi/pyversions/pydantic-xml.svg
    :target: https://pypi.org/project/pydantic-xml
    :alt: Supported Python versions
.. image:: https://codecov.io/gh/dapper91/pydantic-xml/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dapper91/pydantic-xml
    :alt: Code coverage
.. image:: https://readthedocs.org/projects/pydantic-xml/badge/?version=stable&style=flat
   :alt: ReadTheDocs status
   :target: https://pydantic-xml.readthedocs.io


``pydantic-xml`` is a `pydantic <https://docs.pydantic.dev>`_ extension providing model fields xml binding
and xml serialization / deserialization.
It is closely integrated with ``pydantic`` which means it supports most of its features.


Features
--------

- pydantic v1 / v2 support
- flexable attributes, elements and text binding
- python collection types support (``Dict``, ``TypedDict``, ``List``, ``Set``, ``Tuple``, ...)
- ``Union`` type support
- pydantic `generic models <https://docs.pydantic.dev/latest/usage/models/#generic-models>`_ support
- pydantic `computed fields <https://docs.pydantic.dev/latest/usage/computed_fields/>`_ support
- `lxml <https://lxml.de/>`_ xml parser support
- ``xml.etree.ElementTree`` standard library xml parser support

What is not supported?
______________________

- `dataclasses <https://docs.pydantic.dev/usage/dataclasses/>`_

Getting started
---------------

The following model fields binding:

.. code-block:: python

   class Product(BaseXmlModel):
       status: Literal['running', 'development'] = attr()  # extracted from the 'status' attribute
       launched: Optional[int] = attr(default=None)  # extracted from the 'launched' attribute
       title: str  # extracted from the element text


   class Company(BaseXmlModel):
       trade_name: str = attr(name='trade-name')  # extracted from the 'trade-name' attribute
       website: HttpUrl = element()  # extracted from the 'website' element text
       products: List[Product] = element(tag='product', default=[])  # extracted from the 'Company' element's children

defines the XML document:

.. code-block:: xml

   <Company trade-name="SpaceX">
       <website>https://www.spacex.com</website>
       <product status="running" launched="2013">Several launch vehicles</product>
       <product status="running" launched="2019">Starlink</product>
       <product status="development">Starship</product>
   </Company>


See `documentation <https://pydantic-xml.readthedocs.io>`_ for more details.
