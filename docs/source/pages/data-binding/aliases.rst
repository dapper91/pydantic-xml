.. _aliases:

Pydantic aliases
________________

Aliased fields
**************

``pydantic`` library allows to set the alias for a field that is used during serialization/deserialization
instead of the field name. ``pydantic-xml`` respects field aliases too:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/aliases.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/aliases.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/aliases.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Template models
***************

``pydantic`` aliases make it possible to declare so-called template models.
The base model implements the data-validation and data-processing logic but
the fields mapping is described in the inherited classes:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_template.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_template.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_template.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
