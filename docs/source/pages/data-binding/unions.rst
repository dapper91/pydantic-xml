.. _unions:


Union types
___________

To declare a field that can be of one type or anther :py:obj:`typing.Union` is used.
It works for primitive types and models as well but not combined together.

The type declaration order matters.
Currently, ``pydantic`` has two validation modes:

- ``left_to_right``, where the first successful validation is accepted,
- ``smart`` (default), the first type that matches (without coercion) wins.

You can read more about it in the
`pydantic docs <https://docs.pydantic.dev/latest/api/standard_library_types/#union>`_.

Primitive types
***************

Union can be applied to a text, attributes or elements.

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

Union can be applied to model types either.

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


Discriminated unions
********************

Pydantic supports so called
`discriminated unions <https://docs.pydantic.dev/latest/usage/types/unions/#discriminated-unions-aka-tagged-unions>`_ -
the unions where the sub-model type is selected based on its field value.

``pydantic-xml`` supports the similar mechanism to distinguish one sub-model from another by its xml attribute value:


.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/union_discriminated.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/union_discriminated.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/union_discriminated.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
