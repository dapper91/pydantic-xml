import abc
import dataclasses as dc
import typing
from collections import ChainMap
from enum import IntEnum
from functools import cached_property
from typing import Any, Dict, Optional, Tuple

from pydantic_core import core_schema as pcs

from pydantic_xml.element import SearchMode, XmlElementReader, XmlElementWriter
from pydantic_xml.errors import ModelError
from pydantic_xml.typedefs import EntityLocation, Location, NsMap
from pydantic_xml.utils import select_ns

from . import factories


def encode_primitive(value: Any) -> str:
    if value is None:
        return ''
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)


class SchemaTypeFamily(IntEnum):
    META = 0
    PRIMITIVE = 1
    MODEL = 2
    HOMOGENEOUS_COLLECTION = 3
    TUPLE = 4
    MAPPING = 5
    TYPED_MAPPING = 6
    UNION = 7
    TAGGED_UNION = 8
    DEFINITIONS = 9
    DEFINITION_REF = 10
    JSON_OR_PYTHON = 11
    IS_INSTANCE = 12


TYPE_FAMILY = {
    'none':             SchemaTypeFamily.PRIMITIVE,
    'bool':             SchemaTypeFamily.PRIMITIVE,
    'int':              SchemaTypeFamily.PRIMITIVE,
    'float':            SchemaTypeFamily.PRIMITIVE,
    'str':              SchemaTypeFamily.PRIMITIVE,
    'bytes':            SchemaTypeFamily.PRIMITIVE,
    'enum':             SchemaTypeFamily.PRIMITIVE,
    'date':             SchemaTypeFamily.PRIMITIVE,
    'time':             SchemaTypeFamily.PRIMITIVE,
    'datetime':         SchemaTypeFamily.PRIMITIVE,
    'timedelta':        SchemaTypeFamily.PRIMITIVE,
    'uuid':             SchemaTypeFamily.PRIMITIVE,
    'decimal':          SchemaTypeFamily.PRIMITIVE,
    'url':              SchemaTypeFamily.PRIMITIVE,
    'multi-host-url':   SchemaTypeFamily.PRIMITIVE,
    'json':             SchemaTypeFamily.PRIMITIVE,
    'literal':          SchemaTypeFamily.PRIMITIVE,
    'lax-or-strict':    SchemaTypeFamily.PRIMITIVE,

    'is-instance':      SchemaTypeFamily.IS_INSTANCE,

    'model':            SchemaTypeFamily.MODEL,

    'tuple':            SchemaTypeFamily.TUPLE,
    'list':             SchemaTypeFamily.HOMOGENEOUS_COLLECTION,
    'set':              SchemaTypeFamily.HOMOGENEOUS_COLLECTION,
    'frozenset':        SchemaTypeFamily.HOMOGENEOUS_COLLECTION,

    'dict':             SchemaTypeFamily.MAPPING,
    'typed-dict':       SchemaTypeFamily.TYPED_MAPPING,

    'union':            SchemaTypeFamily.UNION,
    'tagged-union':     SchemaTypeFamily.TAGGED_UNION,

    'function-before':  SchemaTypeFamily.META,
    'function-after':   SchemaTypeFamily.META,
    'function-wrap':    SchemaTypeFamily.META,
    'function-plain':   SchemaTypeFamily.META,
    'default':          SchemaTypeFamily.META,
    'nullable':         SchemaTypeFamily.META,

    'definitions':      SchemaTypeFamily.DEFINITIONS,
    'definition-ref':   SchemaTypeFamily.DEFINITION_REF,

    'json-or-python':   SchemaTypeFamily.JSON_OR_PYTHON,
}


class XmlEntityInfoP(typing.Protocol):
    location: Optional[EntityLocation]
    path: Optional[str]
    ns: Optional[str]
    nsmap: Optional[NsMap]
    nillable: bool
    wrapped: Optional['XmlEntityInfoP']


class Serializer(abc.ABC):
    @dc.dataclass(frozen=True)
    class Context:
        model_name: str
        field_name: Optional[str] = None
        field_alias: Optional[str] = None
        field_computed: bool = False
        entity_info: Optional[XmlEntityInfoP] = None

        namespaced_attrs: bool = False
        search_mode: SearchMode = SearchMode.STRICT

        optional: bool = False
        has_default: bool = False
        definitions: Dict[str, pcs.CoreSchema] = dc.field(default_factory=dict)

        parent_ctx: Optional['Serializer.Context'] = None

        @property
        def top(self) -> bool:
            return self.parent_ctx is None

        @property
        def entity_location(self) -> Optional[EntityLocation]:
            return self.entity_info.location if self.entity_info is not None else None

        @property
        def entity_path(self) -> Optional[str]:
            return self.entity_info.path if self.entity_info is not None else None

        @property
        def entity_ns(self) -> Optional[str]:
            return self.entity_info.ns if self.entity_info is not None else None

        @property
        def entity_nsmap(self) -> Optional[NsMap]:
            return self.entity_info.nsmap if self.entity_info is not None else None

        @property
        def nillable(self) -> bool:
            return self.entity_info.nillable if self.entity_info is not None else False

        @property
        def entity_wrapped(self) -> Optional['XmlEntityInfoP']:
            return self.entity_info.wrapped if self.entity_info is not None else None

        @cached_property
        def parent_ns(self) -> Optional[str]:
            if parent_ctx := self.parent_ctx:
                ns = select_ns(parent_ctx.entity_ns, parent_ctx.parent_ns)
                return ns

            return None

        @cached_property
        def parent_nsmap(self) -> Optional[NsMap]:
            if parent_ctx := self.parent_ctx:
                return {
                    **(parent_ctx.entity_nsmap or {}),
                    **(parent_ctx.parent_nsmap or {}),
                }

            return None

        def child(self, **kwargs: Any) -> 'Serializer.Context':
            """
            Creates child context.

            :param kwargs: context variables to be replaced
            """

            return dc.replace(self, parent_ctx=self, **kwargs)

        def replace(self, **kwargs: Any) -> 'Serializer.Context':
            return dc.replace(self, **kwargs)

    @classmethod
    def parse_core_schema(cls, schema: pcs.CoreSchema, ctx: Context) -> 'Serializer':
        schema, ctx = cls.preprocess_schema(schema, ctx)
        return cls.select_serializer(schema, ctx)

    @classmethod
    def preprocess_schema(cls, schema: pcs.CoreSchema, ctx: Context) -> Tuple[pcs.CoreSchema, Context]:
        schema_type = schema['type']
        if (type_family := TYPE_FAMILY.get(schema_type)) is None:
            raise ModelError(f"type {schema_type} is not supported")

        if type_family is SchemaTypeFamily.META:
            if schema_type == 'default':
                ctx = ctx.replace(has_default=True)
            elif schema_type == 'nullable':
                ctx = ctx.replace(optional=True)

            inner_schema = schema['schema']
            return cls.preprocess_schema(inner_schema, ctx)

        elif type_family is SchemaTypeFamily.JSON_OR_PYTHON:
            inner_schema = schema['python_schema']
            return cls.preprocess_schema(inner_schema, ctx)

        elif type_family is SchemaTypeFamily.DEFINITIONS:
            schema = typing.cast(pcs.DefinitionsSchema, schema)
            definitions = {
                definition['ref']: definition
                for definition in schema['definitions']
            }
            ctx = ctx.replace(definitions=ChainMap(definitions, ctx.definitions))

            return cls.preprocess_schema(schema['schema'], ctx)

        elif type_family is SchemaTypeFamily.DEFINITION_REF:
            schema = typing.cast(pcs.DefinitionReferenceSchema, schema)
            schema_ref = schema['schema_ref']
            if typed_schema := ctx.definitions.get(schema_ref):
                return cls.preprocess_schema(typed_schema, ctx)
            else:
                raise ModelError(f"schema reference {schema_ref} not found")

        return schema, ctx

    @classmethod
    def select_serializer(cls, schema: pcs.CoreSchema, ctx: Context) -> 'Serializer':
        schema_type = schema['type']

        if (type_family := TYPE_FAMILY.get(schema_type)) is None:
            raise ModelError(f"type {schema_type} is not supported")

        if ctx.entity_location is EntityLocation.WRAPPED:
            return factories.wrapper.from_core_schema(schema, ctx)

        if type_family is SchemaTypeFamily.PRIMITIVE:
            schema = typing.cast(factories.primitive.PrimitiveTypeSchema, schema)
            return factories.primitive.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.MODEL:
            schema = typing.cast(pcs.ModelSchema, schema)
            return factories.model.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.HOMOGENEOUS_COLLECTION:
            schema = typing.cast(factories.homogeneous.HomogeneousCollectionTypeSchema, schema)
            return factories.homogeneous.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.TUPLE:
            schema = typing.cast(pcs.TupleSchema, schema)
            return factories.tuple.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.MAPPING:
            schema = typing.cast(pcs.DictSchema, schema)
            return factories.mapping.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.TYPED_MAPPING:
            schema = typing.cast(pcs.TypedDictSchema, schema)
            return factories.typed_mapping.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.UNION:
            schema = typing.cast(pcs.UnionSchema, schema)
            return factories.union.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.TAGGED_UNION:
            schema = typing.cast(pcs.TaggedUnionSchema, schema)
            return factories.tagged_union.from_core_schema(schema, ctx)

        elif type_family is SchemaTypeFamily.IS_INSTANCE:
            schema = typing.cast(pcs.IsInstanceSchema, schema)
            return factories.is_instance.from_core_schema(schema, ctx)

        else:
            raise AssertionError("unreachable")

    @abc.abstractmethod
    def serialize(
            self, element: XmlElementWriter, value: Any, encoded: Any, *, skip_empty: bool = False,
    ) -> Optional[XmlElementWriter]:
        """
        Serializes a value to the provided xml element.

        :param element: xml element the value is serialized to
        :param value: original value
        :param encoded: encoded value (encoded by pydantic)
        :param skip_empty: skip empty element
        :return: created sub-element or original one if sub-element has not been created
        """

    @abc.abstractmethod
    def deserialize(
            self,
            element: Optional[XmlElementReader],
            *,
            context: Optional[Dict[str, Any]],
            sourcemap: Dict[Location, int],
            loc: Location,
    ) -> Optional[Any]:
        """
        Deserializes a value from the xml element.

        :param element: xml element the value is deserialized from
        :param context: pydantic validation context
        :param sourcemap: source-to-element mapping
        :param loc: entity location
        :return: deserialized value
        """
