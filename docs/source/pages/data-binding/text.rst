.. _text:

Text
____

Primitive types
***************

A field of a primitive type is bound to the local element text.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/text_primitive.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/text_primitive.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/text_primitive.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end

**Note**: the empty element text is deserialized as ``None`` not as an empty string:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/text_primitive_optional.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/text_primitive_optional.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/text_primitive_optional.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end

To have an empty string instead add ``""`` as a default value:

.. code-block:: python

    class Company(BaseXmlModel):
        description: str = ""
