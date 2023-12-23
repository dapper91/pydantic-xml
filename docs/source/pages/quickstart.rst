.. _quickstart:


Quickstart
~~~~~~~~~~

Base model
__________

To declare an xml serializable / deserializable model inherit it
from :py:class:`pydantic_xml.BaseXmlModel` base class. It collects the
data binding meta-information and generates an xml serializer for the model.

To serialize the object into an xml string use :py:meth:`pydantic_xml.BaseXmlModel.to_xml` method or
:py:meth:`pydantic_xml.BaseXmlModel.from_xml` to deserialize it.
For more information see :ref:`XML serialization <pages/misc:xml serialization>`.

Data binding
____________

A model field can be bound to an xml attribute, element or text. Binding type is derived using the following rules:

1. Primitives
*************

field of a primitive type (``int``, ``float``, ``str``, ``datetime``, ...)
is bound to the element text by default:

.. literalinclude:: ../../../examples/snippets/text_primitive.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/text_primitive.py
  :language: python
  :start-after: model-start
  :end-before: model-end

To alter the default behaviour the field has to be marked as :py:func:`pydantic_xml.attr`:

.. literalinclude:: ../../../examples/snippets/attribute.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/attribute.py
  :language: python
  :start-after: model-start
  :end-before: model-end

or :py:func:`pydantic_xml.element`:

.. literalinclude:: ../../../examples/snippets/element_primitive.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/element_primitive.py
  :language: python
  :start-after: model-start
  :end-before: model-end

For more information see :ref:`text <pages/data-binding/text:primitive types>`,
:ref:`attributes <pages/data-binding/attributes:primitive types>` and
:ref:`elements <pages/data-binding/elements:primitive types>` bindings declarations.


2. Sub-models
*************

field of a model type (inherited from ``BaseXmlModel``) is bound to a sub-element:

.. literalinclude:: ../../../examples/snippets/element_model.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/element_model.py
  :language: python
  :start-after: model-start
  :end-before: model-end

For more information see :ref:`model types<pages/data-binding/elements:model types>`.


3. Mapping
**********

field of a mapping type (``Dict[str, str]``, ``Mapping[str, int]``, ``TypedDict`` ...) is bound to local element
attributes (by default):

.. literalinclude:: ../../../examples/snippets/mapping.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/mapping.py
  :language: python
  :start-after: model-start
  :end-before: model-end

or to sub-element attributes if the field is marked as :py:func:`pydantic_xml.element`:

.. literalinclude:: ../../../examples/snippets/mapping_element.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/mapping_element.py
  :language: python
  :start-after: model-start
  :end-before: model-end

For more information see :ref:`mappings <pages/data-binding/mappings:mappings>`.


4. Primitive collection
***********************

field of a primitive collection type (``List[str]``, ``Set[int]``, ``Tuple[float, float]`` ...) is bound to
sub-elements texts:

.. literalinclude:: ../../../examples/snippets/homogeneous_primitives.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/homogeneous_primitives.py
  :language: python
  :start-after: model-start
  :end-before: model-end

For more information see
:ref:`primitive heterogeneous collections <pages/data-binding/heterogeneous:heterogeneous collections>`.


5. Model collection
*******************

field of a model collection type (``List[BaseXmlModel]``, ``Tuple[BaseXmlModel, ...]``) is bound to
sub-elements:

.. literalinclude:: ../../../examples/snippets/homogeneous_models.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/homogeneous_models.py
  :language: python
  :start-after: model-start
  :end-before: model-end

For more information see
:ref:`primitive homogeneous collections <pages/data-binding/homogeneous:model homogeneous collection>` and
:ref:`primitive heterogeneous collections <pages/data-binding/heterogeneous:heterogeneous collections>`.


6. Wrapper
**********

wrapped field (marked as :py:func:`pydantic_xml.wrapped`) is bound to a sub-element located
at the provided path. Then depending on the field type the rules are the same as described above:

.. literalinclude:: ../../../examples/snippets/wrapper.py
  :language: xml
  :lines: 2-
  :start-after: xml-start
  :end-before: xml-end

.. literalinclude:: ../../../examples/snippets/wrapper.py
  :language: python
  :start-after: model-start
  :end-before: model-end

For more information see :ref:`wrapped entities <pages/data-binding/wrapper:wrapped entities>`


Example
_______

The following example illustrates all the previously described rules combined with some ``pydantic`` features:

*doc.xml:*

.. literalinclude:: ../../../examples/quickstart/doc.xml
    :language: xml

*model.py:*

.. literalinclude:: ../../../examples/quickstart/model.py
    :language: python


JSON
____


Since ``pydantic`` supports json serialization ``pydantic-xml`` can be used as xml-to-json transcoder:

.. code-block:: python

    ...

    xml_doc = pathlib.Path('./doc.xml').read_text()
    company = Company.from_xml(xml_doc)

    json_doc = pathlib.Path('./doc.json')
    json_doc.write_text(company.json(indent=4))

*doc.json:*

.. literalinclude:: ../../../examples/quickstart/doc.json
    :language: json
