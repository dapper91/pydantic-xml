.. _generics:


Generic models
______________

``pydantic`` library supports `generic-models <https://docs.pydantic.dev/latest/usage/models/#generic-models>`_.
Generic xml model can be declared the same way:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_generic.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML1

                .. literalinclude:: ../../../../examples/snippets/model_generic.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON1

                .. literalinclude:: ../../../../examples/snippets/model_generic.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end

            .. tab-item:: XML2

                .. literalinclude:: ../../../../examples/snippets/model_generic.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start-2
                    :end-before: xml-end-2

            .. tab-item:: JSON2

                .. literalinclude:: ../../../../examples/snippets/model_generic.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start-2
                    :end-before: json-end-2


A generic model can be of one or more types and organized in a recursive structure.
The following example illustrates how to describe a flexible SOAP request model:

*model.py:*

.. literalinclude:: ../../../../examples/generic-model/model.py
    :language: python

*doc.xml:*

.. literalinclude:: ../../../../examples/generic-model/doc.xml
    :language: xml

*doc.json:*

.. literalinclude:: ../../../../examples/generic-model/doc.json
    :language: json
