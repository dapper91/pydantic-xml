.. _raw_fields:


Raw fields
__________

Raw element typed fields
************************

The library supports raw xml elements. It is helpful when the element schema is unknown or its schema is too complex
to define a model describing it.

To declare a raw element field annotate it with :py:class:`xml.etree.ElementTree.Element`
(or :py:class:`lxml.etree._Element` for ``lxml``).

Since ``pydantic`` doesn't support arbitrary types by default it is necessary to allow them
by setting ``arbitrary_types_allowed`` flag.
See `documentation <https://docs.pydantic.dev/latest/usage/model_config/#arbitrary-types-allowed>`_ for more details.


.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/element_raw.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: input XML

                .. literalinclude:: ../../../../examples/snippets/element_raw.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start-1
                    :end-before: xml-end-1

            .. tab-item:: output XML

                .. literalinclude:: ../../../../examples/snippets/element_raw.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start-2
                    :end-before: xml-end-2
