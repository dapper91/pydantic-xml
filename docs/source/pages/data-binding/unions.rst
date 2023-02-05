.. _unions:


Union types
___________

To declare a field that can be of one type or anther :py:obj:`typing.Union` is used.
It works for primitive types and models as well but not combined together.


Primitive types
***************

Union can be applied to text, attributes or elements. The type declaration order matters
since the first type matched wins.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/union_primitives.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/union_primitives.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/union_primitives.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Model types
***********

Union can be applied to model types either. The type declaration order matters
since the first model matched wins.


.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/union_models.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/union_models.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/union_models.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
