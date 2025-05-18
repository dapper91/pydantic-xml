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


Custom xml serialization
________________________

``pydantic-xml`` provides functional serializers and validators to customise how a field is serialized to xml
or validated from it. Use :py:func:`pydantic_xml.xml_field_serializer` decorator to mark a method as an xml serializer
or :py:func:`pydantic_xml.xml_field_serializer` decorators to mark it as an xml validator.

The following example illustrate how to serialize ``xs:list`` element:

*model.py:*

.. literalinclude:: ../../../examples/xml-serialization-decorator/model.py
    :language: python

*doc.xml:*

.. literalinclude:: ../../../examples/xml-serialization-decorator/doc.xml
    :language: xml


``pydantic-xml`` also supports the ``Annotated`` typing form to attach metadata to an annotation:

*model.py:*

.. literalinclude:: ../../../examples/xml-serialization-annotation/model.py
    :language: python


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

It is also possible to exclude ``None`` values:

.. literalinclude:: ../../../examples/snippets/exclude_none.py
    :language: python
    :start-after: model-start
    :end-before: model-end

.. literalinclude:: ../../../examples/snippets/exclude_none.py
    :language: xml
    :lines: 2-
    :start-after: xml-start
    :end-before: xml-end


... or unset values:

.. literalinclude:: ../../../examples/snippets/exclude_unset.py
    :language: python
    :start-after: model-start
    :end-before: model-end

.. literalinclude:: ../../../examples/snippets/exclude_unset.py
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


Dynamic model creation
~~~~~~~~~~~~~~~~~~~~~~

There are some cases when it is necessary to create a model using runtime information to describe model fields.
For this ``pydantic-xml`` provides the :py:func:`pydantic_xml.create_model` function to create a model on the fly:

.. literalinclude:: ../../../examples/snippets/dynamic_model_creation.py
    :language: python
    :start-after: model-start
    :end-before: model-end

Field specification syntax is similar to ``pydantic`` one. For more information
see the `documentation <https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation>`_.


Document type declaration
~~~~~~~~~~~~~~~~~~~~~~~~~

A document type declaration is an instruction that associates a particular XML document
with a document type definition (DTD).

DTD is supported by ``lxml`` backend only so the library doesn't provide an api for that natively,
but it can be easily implemented by your hand:

.. code-block:: python

    from typing import Any, ClassVar, Union

    import pydantic_xml as pxml
    import lxml.etree


    class DTDXmlModel(pxml.BaseXmlModel):
        DOC_PUBLIC_ID: ClassVar[str]
        DOC_SYSTEM_URL: ClassVar[str]

        def to_xml(
                self,
                *,
                skip_empty: bool = False,
                exclude_none: bool = False,
                exclude_unset: bool = False,
                **kwargs: Any,
        ) -> Union[str, bytes]:
            root = self.to_xml_tree(skip_empty=skip_empty, exclude_none=exclude_none, exclude_unset=exclude_unset)
            tree = lxml.etree.ElementTree(root)
            tree.docinfo.public_id = self.DOC_PUBLIC_ID
            tree.docinfo.system_url = self.DOC_SYSTEM_URL

            return lxml.etree.tostring(tree, **kwargs)


    class Html(DTDXmlModel, tag='html'):
        DOC_PUBLIC_ID: ClassVar[str] = '-//W3C//DTD HTML 4.01//EN'
        DOC_SYSTEM_URL: ClassVar[str] = 'http://www.w3.org/TR/html4/strict.dtd'

        title: str = pxml.wrapped('head', pxml.element())
        body: str = pxml.element()


    html_doc = Html(title="This is a title", body="Hello world!")
    xml = html_doc.to_xml(pretty_print=True)

    print(xml.decode())


.. code-block:: xml

    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
      <head>
        <title>This is a title</title>
      </head>
      <body>Hello world!</body>
    </html>


Mypy
~~~~

``pydantic-xml`` provides a ``mypy`` plugin that adds some important pydantic-specific features to type-check your code.

To enable the plugin add the following to your ``mypy.ini`` config file:

.. code-block:: ini

    [mypy]
    plugins = pydantic_xml.mypy

or ``pyproject.toml``:

.. code-block:: toml

    [tool.mypy]
    plugins = [
      "pydantic_xml.mypy"
    ]
