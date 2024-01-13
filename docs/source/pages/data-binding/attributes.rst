.. _attributes:


Attributes
__________

Primitive types
***************

A field of a primitive type marked as :py:func:`pydantic_xml.attr` is bound to a local element attribute.
Parameter ``name`` is used to declare the attribute name from which the data is extracted.
If it is omitted the field name is used (respecting ``pydantic`` field aliases).

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/attribute.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/attribute.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/attribute.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Namespaces
**********

The namespace can be defined for attributes as well. To bind a model field to a namespaced attribute
pass parameter ``ns`` to a :py:func:`pydantic_xml.attr` and define a namespace map for the model.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/attribute_namespace.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/attribute_namespace.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/attribute_namespace.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Namespace inheritance
*********************

The attribute namespace can be inherited from the model.
To make attributes inherit the model namespace define the model-level namespace and namespace map
and set ``ns_attrs`` flag.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/attribute_namespace_inheritance.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/attribute_namespace_inheritance.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/attribute_namespace_inheritance.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
