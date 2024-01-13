.. _misc:


Encoding
~~~~~~~~


Custom type encoding
____________________

``pydantic`` provides mechanisms to `customize <https://docs.pydantic.dev/latest/usage/serialization/#custom-serializers>`_
the default json encoding format. ``pydantic-xml`` uses custom encoders during the xml serialization too:

.. code-block:: python

    class File(BaseXmlModel):
        created: datetime = element()

        @field_serializer('created')
        def encode_created(self, value: datetime) -> float:
            return value.timestamp()


The following example illustrate how to encode :py:class:`bytes` typed fields as Base64 string
during the xml serialization:

*model.py:*

.. literalinclude:: ../../../examples/custom-encoder/model.py
    :language: python

*file1.txt:*

.. literalinclude:: ../../../examples/custom-encoder/file1.txt

*file2.txt:*

.. literalinclude:: ../../../examples/custom-encoder/file2.txt

*doc.xml:*

.. literalinclude:: ../../../examples/custom-encoder/doc.xml
    :language: xml


Optional type encoding
~~~~~~~~~~~~~~~~~~~~~~

Since the xml format doesn't support ``null`` type natively it is not obvious how to encode ``None`` fields
(ignore it, encode it as an empty string or mark it as ``xsi:nil``).

``None`` values are encoded as empty strings by default, but the library provides some alternative ways:

- Define your own encoding format for ``None`` values:

.. literalinclude:: ../../../examples/snippets/py3.9/serialization.py
  :language: python


- Mark an empty elements as `nillable <https://www.w3.org/TR/xmlschema-1/#xsi_nil>`_:

.. literalinclude:: ../../../examples/snippets/serialization_nillable.py
  :language: python


- Drop empty elements at all:

.. code-block:: python

    from typing import Optional
    from pydantic_xml import BaseXmlModel, element

    class Company(BaseXmlModel, skip_empty=True):
        title: Optional[str] = element(default=None)


    company = Company()
    assert company.to_xml() == b'<Company/>'


Empty entities exclusion
~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to exclude all empty entities from the resulting xml document at once. To do that
just pass ``skip_empty=True`` parameter to :py:meth:`pydantic_xml.BaseXmlModel.to_xml` during the serialization.
That parameter is applied to the root model and all its sub-models by default. But it can be adjusted
for a particular model during its declaration as illustrated in the following example:

.. literalinclude:: ../../../examples/snippets/skip_empty.py
    :language: python
    :start-after: model-start
    :end-before: model-end

.. literalinclude:: ../../../examples/snippets/skip_empty.py
    :language: xml
    :lines: 2-
    :start-after: xml-start
    :end-before: xml-end


Default namespace
~~~~~~~~~~~~~~~~~

Xml default namespace is a namespace that is applied to the element and all its sub-elements
without explicit definition.

In the following example the element ``company`` has no explicit namespace but the default namespace for that
element and all its sub-elements is ``http://www.company.com/co``. ``contacts`` element has no explicit
namespace either but it doesn't inherit it from ``company`` because it has its own default namespace.
The same goes for ``socials`` element except that its sub-elements inherit a namespace from the parent:

.. literalinclude:: ../../../examples/snippets/default_namespace.py
    :language: xml
    :lines: 2-
    :start-after: xml-start
    :end-before: xml-end

A model for that document can be described like this:

.. literalinclude:: ../../../examples/snippets/default_namespace.py
    :language: python
    :start-after: model-start
    :end-before: model-end

Look at the model's parameter ``nsmap``. To set a default namespace for a model and its sub-fields
pass that namespace by an empty key.

.. admonition:: Default namespace serialization
   :class: important

   Standard libray xml serializer has a default namespace serialization problem: it doesn't respect
   default namespaces definition moving namespaces definition to the root element substituting them with
   ``ns{0..}`` namespaces:

   .. code-block:: xml

       <ns0:company xmlns:ns0="http://www.company.com/co"
                    xmlns:ns1="http://www.company.com/cnt"
                    xmlns:ns2="http://www.company.com/soc">
           <ns1:contacts>
               <ns2:socials>
                   <ns2:social>https://www.linkedin.com/company/spacex</ns2:social>
                   <ns2:social>https://twitter.com/spacex</ns2:social>
                   <ns2:social>https://www.youtube.com/spacex</ns2:social>
               </ns2:socials>
           </ns1:contacts>
       </ns0:company>

   That document is still correct but some parsers require namespace declaration kept untouched. To avoid
   that use ``lxml`` as a serialization backed since it doesn't have that kind of problem.
   See :ref:`lxml installation <pages/installation:optional dependencies>`.


Computed entities
~~~~~~~~~~~~~~~~~

``pydantic`` supports `computed fields <https://docs.pydantic.dev/latest/usage/computed_fields/>`_.
Computed fields allow property and cached_property to be included when serializing models or dataclasses.
This is useful for fields that are computed from other fields,
or for fields that are expensive to compute and should be cached.

``pydantic-xml`` provides similar api for xml entities: text, attribute or element properties can be
included into the xml document during serialization. To make a property computable decorate it with
``pydantic.computed_field`` to bind it to the current element,
:py:func:`pydantic_xml.computed_attr` to bind it to an attribute or
:py:func:`pydantic_xml.computed_element` to bind it to a sub-element.

The document:

*doc.xml:*

.. literalinclude:: ../../../examples/computed-entities/doc.xml
    :language: xml


produced by the following model:

*model.py:*

.. literalinclude:: ../../../examples/computed-entities/model.py
    :language: python



XML parser
~~~~~~~~~~

``pydantic-xml`` tries to use the fastest xml parser in your system. It uses ``lxml`` if it is installed
in your environment otherwise falls back to the standard library xml parser.

To force ``pydantic-xml`` to use standard :py:mod:`xml.etree.ElementTree` xml parser set ``FORCE_STD_XML``
environment variable.


XML serialization
~~~~~~~~~~~~~~~~~

XML serialization process is customizable depending on which backend you use.
For example ``lxml`` can pretty-print the output document or serialize it using a particular encoding
(for more information see :py:func:`lxml.etree.tostring`).
To set that parameters pass them to :py:meth:`pydantic_xml.BaseXmlModel.to_xml` as extra arguments:

.. code-block:: python

   xml = obj.to_xml(
       pretty_print=True,
       encoding='UTF-8',
       standalone=True
   )

   print(xml)


Standard library serializer also supports customizations.
For more information see :py:func:`xml.etree.ElementTree.tostring`,
