.. _models:


Model
_____

Root model
**********

A root model is bound to the root xml element with the tag matching the model ``tag`` or class name.
If the corresponding element not found :py:class:`pydantic_xml.ParsingError` exception is raised.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_root.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_root.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_root.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Sub-models
**********

See :ref:`models <pages/data-binding/elements:model types>`.


Namespaces
**********

You can declare the root model namespace by setting parameters ``ns`` and ``nsmap``.
where ``ns`` is the element namespace alias and ``nsmap`` is a namespace mapping.
The namespace mapping is inherited by all the model field:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/element_namespace_global.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/element_namespace_global.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/element_namespace_global.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Custom root type
****************

``Pydantic`` supports so-called `custom root type <https://docs.pydantic.dev/latest/usage/models/#rootmodel-and-custom-root-types>`_.

It works for primitive types:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_root_primitive.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_root_primitive.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_root_primitive.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


collection types:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_root_collection.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_root_collection.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_root_collection.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


and model types:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_root_type.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_root_type.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_root_type.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Self-referencing models
***********************

``pydantic`` library supports `self-referencing models <https://docs.pydantic.dev/latest/usage/postponed_annotations/#self-referencing-or-recursive-models>`_.
Within the model, you can refer to a not-yet-constructed model using a string.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_self_ref.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_self_ref.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_self_ref.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


That allows you to parse hierarchical data structures:

*model.py:*

.. literalinclude:: ../../../../examples/self-ref-model/model.py
    :language: python

*doc.xml:*

.. literalinclude:: ../../../../examples/self-ref-model/doc.xml
    :language: xml

*doc.json:*

.. literalinclude:: ../../../../examples/self-ref-model/doc.json
    :language: json
