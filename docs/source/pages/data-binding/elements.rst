.. _elements:


Elements
________

Primitive types
***************

A field of a primitive type marked as :py:func:`pydantic_xml.element` is bound to the sub-element text.
Parameter ``tag`` is used to declare the sub-element tag to which the field is bound.
If it is omitted the field name is used (respecting ``pydantic`` field aliases).

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/element_primitive.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/element_primitive.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/element_primitive.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Model types
***********

A field of a model type marked as :py:func:`pydantic_xml.element` is bound to a sub-element.
Then the sub-element is used as the root for that sub-model. For more information
see :ref:`model data binding <pages/data-binding/models:model>`.
Parameter ``tag`` is used to declare a sub-element tag to which the sub-model is bound.
If it is omitted the sub-model ``tag`` setting is used.
If it is omitted too the field name is used (respecting ``pydantic`` field aliases).
So the order is the following: element tag, model tag, field alias, field name.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/element_model.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/element_model.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/element_model.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Namespaces
**********

You can declare the element namespace passing parameters ``ns`` and ``nsmap`` to :py:func:`pydantic_xml.element`
where ``ns`` is the element namespace alias and ``nsmap`` is a namespace mapping:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/element_namespace.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/element_namespace.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/element_namespace.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end

The namespace and namespace mapping can be declared for a model. In that case all fields
:ref:`except attributes <pages/data-binding/attributes:namespace inheritance>` inherit them:

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


The namespace and namespace mapping can be also applied to model types passing ``ns`` and ``nsmap``
to :py:func:`pydantic_xml.element`. If they are omitted the model namespace and namespace mapping is used:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/element_namespace_model.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/element_namespace_model.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/element_namespace_model.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Elements search mode
********************

A model supports several element search strategies (modes). Each strategy has its own pros and cons.

Strict (default)
................

The element to which a field will be bound is searched sequentially one by one (without skipping unknown elements).
If the tag of a next element doesn't match the field tag that field is considered unbound.
This mode is used when the strong document validation is required. If you parse a large document it is the best
choice because it works in predictable time since it doesn't require any look-ahead operations.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/lxml/model_mode_strict.py
            :language: python
            :start-after: model-start
            :end-before: model-end

        .. error::
              code raises an exception because of the incorrect field order

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/lxml/model_mode_strict.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/lxml/model_mode_strict.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end


Ordered
.......

The element to which a field will be bound is searched sequentially skipping unknown elements.
If the tag of the next element doesn't match the field tag that element is skipped and the search continues.
This mode is used when the elements order matters but unexpected (or irrelevant) elements could appear in a document.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_mode_ordered.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_mode_ordered.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_mode_ordered.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end

.. warning::
    This mode could lead to some unexpected results. For example the following model:

    .. code-block:: python

       class Model(BaseXmlModel, search_mode='ordered'):
           field1: Optional[str] = element(tag='element1')
           field2: str = element(tag='element2')
           field3: str = element(tag='element1')

    fails for the following document:

    .. code-block:: xml

       <Model>
           <element2>value</element2>
           <element1>value</element2>
       </Model>

    because the first field will be bound to the second element (the algorithm looks ahead until the first match found,
    which is the second element) and the second field will not be bound to any element.


Unordered
.........

The element to which a field will be bound is searched among all sub-elements in any order.
This mode is used when the elements order doesn't matter.
The time complexity of this strategy in worst case is
``O(F*E)`` where ``F`` - is the number of fields, ``E`` - the number of sub-elements so that it is not suitable
for large documents.

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: Model

        .. literalinclude:: ../../../../examples/snippets/model_mode_unordered.py
            :language: python
            :start-after: model-start
            :end-before: model-end

    .. grid-item-card:: Document

        .. tab-set::

            .. tab-item:: XML

                .. literalinclude:: ../../../../examples/snippets/model_mode_unordered.py
                    :language: xml
                    :lines: 2-
                    :start-after: xml-start
                    :end-before: xml-end

            .. tab-item:: JSON

                .. literalinclude:: ../../../../examples/snippets/model_mode_unordered.py
                    :language: json
                    :lines: 2-
                    :start-after: json-start
                    :end-before: json-end
