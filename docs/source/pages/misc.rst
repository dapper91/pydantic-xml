.. _misc:


Encoding
~~~~~~~~


Custom type encoding
____________________

``pydantic-xml`` uses ``pydantic`` default encoder to encode fields data during xml serialization. To alter the default
behaviour ``pydantic`` provides a mechanism to `customize <https://docs.pydantic.dev/usage/exporting_models/#json_encoders>`_
the default json encoding format for a particular type. ``pydantic-xml`` allows to do the same for xml serialization.
The api is similar to the json one:

.. code-block:: python

    class Model(BaseXmlModel):
        class Config:
            xml_encoders = {
                bytes: base64.b64encode,
            }
        ...


The following example illustrate how to encode :py:class:`bytes` typed fields as Base64 string during xml serialization:

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


None type encoding
__________________

Since xml format doesn't support ``null`` type natively it is not obvious how to encode ``None`` fields
(ignore it, encode it as an empty string or mark it as ``xsi:nil``) the library doesn't implement
``None`` type encoding by default.

You can define your own encoding format for the model:

.. code-block:: python

    from typing import Optional
    from pydantic_xml import BaseXmlModel, element


    class Company(BaseXmlModel):
        class Config:
            xml_encoders = {
                type(None): lambda o: '',  # encodes None field as an empty string
            }

        title: Optional[str] = element()


    company = Company()
    assert company.to_xml() == b'<Company><title /></Company>'


or drop ``None`` fields at all:

.. code-block:: python

    from typing import Optional
    from pydantic_xml import BaseXmlModel, element


    class Company(BaseXmlModel):
        title: Optional[str] = element()


    company = Company()
    assert company.to_xml(skip_empty=True) == b'<Company />'



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
   that use ``lxml`` a as serializer backed since it doesn't have that kind of problem.


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
To set that features pass them to :py:meth:`pydantic_xml.BaseXmlModel.to_xml`

.. code-block:: python

   xml = obj.to_xml(
       pretty_print=True,
       encoding='UTF-8',
       standalone=True
   )

   print(xml)


Standard library serializer also supports customizations.
For more information see :py:func:`xml.etree.ElementTree.tostring`,
