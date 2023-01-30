.. _attributes:


Attributes
__________

Primitive types
***************

Field of a primitive type marked as :py:func:`pydantic_xml.attr` is bound to a  local element attribute.
Parameter ``name`` is used to declare the attribute name from which the data is extracted.
If it is omitted field name is used (respecting ``pydantic`` field aliases).

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

Namespace can be defined for attributes. To bind a model field to a namespaced attribute
pass parameter ``ns`` to a :py:func:`pydantic_xml.attr` and define namespace map for the model.

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

Attribute namespace can be inherited from the model.
To make attributes inherit the model namespace define model-level namespace and namespace map
and set parameter ``ns_attrs``.

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
