.. _wrapper:

Wrapper
_______

Some XML documents have deep element hierarchy which requires to declare a lot of "dumb" sub-models
to extract the deepest element data. :py:func:`pydantic_xml.wrapped` helps to get rid of that boilerplate code.


Wrapped entities
****************

To declare a field bound to a sub-element text, attribute or element mark that field
as :py:func:`pydantic_xml.wrapped` providing it with the sub-element path and the entity type. It can be applied to
a primitive type, model, mapping or collection as well.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/wrapper.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/wrapper.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/wrapper.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Nested wrappers
***************

Wrapper can be wrapped by another wrapper building up a nested structure.
It helps to extract data from sub-elements from different namespaces:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/wrapper_nested.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/wrapper_nested.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/wrapper_nested.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
