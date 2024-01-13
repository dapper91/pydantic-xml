.. _mappings:


Mappings
________

Local attributes
****************

A field of a mapping type is bound to local element attributes.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/mapping.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/mapping.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/mapping.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Sub-element attributes
**********************

A field of a mapping type marked as :py:func:`pydantic_xml.element` is bound to sub-element attributes.
The ``tag`` parameter of :py:func:`pydantic_xml.element` is used as a sub-element tag to which attributes
the field is bound. If it is omitted the field name is used (respecting ``pydantic`` field aliases).

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/mapping_element.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/mapping_element.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/mapping_element.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Typed dict
**********

Fields of :py:class:`typing.TypedDict` type are also supported:


.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/mapping_typed.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/mapping_typed.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/mapping_typed.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
