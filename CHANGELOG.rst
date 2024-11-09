Changelog
=========

2.14.0 (2024-11-09)
-------------------
- union validation error location fixed.
- potential memory leak fixed. See https://github.com/dapper91/pydantic-xml/issues/222.
- python 3.13 support added.


2.13.1 (2024-10-03)
-------------------

- multiple pydantic model validators bug fixed.


2.13.0 (2024-09-29)
-------------------

- custom field xml serializer/validator support added. See https://github.com/dapper91/pydantic-xml/pull/212



2.12.1 (2024-08-26)
-------------------

- collection of tagged union deserialization bug fixed. See https://github.com/dapper91/pydantic-xml/issues/206


2.12.0 (2024-08-24)
-------------------

- exclude_none and exclude_unset serialization flags support added. See https://github.com/dapper91/pydantic-xml/pull/204.


2.11.0 (2024-05-11)
-------------------

- named tuple support added. See https://github.com/dapper91/pydantic-xml/issues/172


2.10.0 (2024-05-09)
-------------------

- dynamic model creation support added. See https://pydantic-xml.readthedocs.io/en/latest/pages/misc.html#dynamic-model-creation


2.9.2 (2024-04-19)
------------------

- mypy plugin dataclass_transform decorated model bug fixed. See https://github.com/dapper91/pydantic-xml/issues/152#issuecomment-2057949479.


2.9.1 (2024-04-12)
------------------

- PEP-681 (Data Class Transforms) support added. See https://github.com/dapper91/pydantic-xml/pull/178.
- pydantic 2.7 enum type support added. See https://github.com/dapper91/pydantic-xml/issues/182


2.9.0 (2024-02-03)
------------------

- pydantic 2.6 incompatibility fixed. See https://github.com/dapper91/pydantic-xml/issues/167.


2.8.1 (2024-01-21)
------------------

- union collection deserialization bug fixed. See https://github.com/dapper91/pydantic-xml/pull/165.


2.8.0 (2024-01-13)
------------------

- mypy plugin added. See https://pydantic-xml.readthedocs.io/en/latest/pages/misc.html#mypy.
- optional raw element bug fixed. See https://github.com/dapper91/pydantic-xml/issues/158.


2.7.0 (2023-12-18)
------------------

- validation errors provide the full path to the malformed field (including nested sub-models).
- error text contain the xml document source line where the error occurred (lxml parser only). See https://github.com/dapper91/pydantic-xml/pull/150.


2.6.0 (2023-12-06)
------------------

- nillable element support added. See https://github.com/dapper91/pydantic-xml/pull/146.


2.5.0 (2023-11-26)
------------------

- adjacent sub-elements support added. See https://github.com/dapper91/pydantic-xml/pull/143.


2.4.0 (2023-11-06)
------------------

- attributes with default namespace bug fixed. See https://github.com/dapper91/pydantic-xml/issues/137.


2.3.0 (2023-10-22)
------------------

- bool type encoding format changed from 'True' to 'true'. See https://github.com/dapper91/pydantic-xml/issues/126.
- None type encoding format changed from 'None' to ''.


2.2.4 (2023-10-06)
------------------

- root model default value bug fixed.
- python 3.12 support added.


2.2.3 (2023-09-20)
------------------

- raw element missing tail bug fixed. See https://github.com/dapper91/pydantic-xml/issues/118.


2.2.2 (2023-09-15)
------------------

- model validator 'before' mode support added.


2.2.1 (2023-09-12)
------------------

- model level `skip_empty` parameter added.
- wrapped element extra entities checking bugs fixed.


2.2.0 (2023-09-07)
------------------

- pydantic extra='forbid' parameter is being applied to xml elements too. See https://github.com/dapper91/pydantic-xml/pull/106.



2.1.0 (2023-08-24)
------------------

- raw element typed fields support added. See https://github.com/dapper91/pydantic-xml/issues/14.
- pydantic field exclude flag bug fixed (works only for serialization now).


2.0.0 (2023-08-19)
------------------

- library upgraded to pydantic version 2. See https://docs.pydantic.dev/2.0/migration/
- generic models are no longer inherited from BaseGenericXmlModel but from BaseXmlModel.
- custom root type declaration has been changed. It must inherit RootXmlModel from now on.
- encoding customization api has been changed. See https://pydantic-xml.readthedocs.io/en/v2.0.0/pages/misc.html#encoding
- element attributes can be bound to TypedDict. See https://pydantic-xml.readthedocs.io/en/v2.0.0/pages/data-binding/mappings.html#typed-dict
- tagged unions support added. See https://pydantic-xml.readthedocs.io/en/v2.0.0/pages/data-binding/unions.html#discriminated-unions
- computed entities support added. See https://pydantic-xml.readthedocs.io/en/v2.0.0/pages/misc.html#computed-entities


2.0.0b3 (2023-08-18)
--------------------

- decimal type support added.
- unparameterized root models serializer generation bug fixed. Affected by https://github.com/pydantic/pydantic/pull/7119.


2.0.0b2 (2023-08-06)
--------------------

- XmlModelMeta accepts ModelMetaclass directly. See https://github.com/dapper91/pydantic-xml/pull/90.


2.0.0b1 (2023-07-30)
--------------------

- tagged unions support added.


2.0.0a2 (2023-07-24)
--------------------

- pydantic validation context support added.


2.0.0a1 (2023-07-15)
--------------------

- library upgraded to pydantic version 2. See https://docs.pydantic.dev/2.0/migration/


1.0.0 (2023-07-14)
------------------

- library api stabilized
- custom root type serialization format changed.

0.7.0 (2023-06-24)
------------------

- from_xml, from_xml_tree methods return type bound to cls type. This resolves the problem with mypy checker.
  See https://github.com/dapper91/pydantic-xml/issues/65
- wrapped sub-elements serialization bug fixed. See https://github.com/dapper91/pydantic-xml/pull/70


0.6.3 (2023-06-19)
------------------

- forward refs support added. See https://github.com/dapper91/pydantic-xml/pull/61


0.6.2 (2023-06-10)
------------------

- piped union typehints support added. See https://github.com/dapper91/pydantic-xml/issues/56


0.6.1 (2023-04-15)
------------------

- model parameters inheritance bug fixed. See https://github.com/dapper91/pydantic-xml/issues/51


0.6.0 (2023-02-05)
------------------

- union types support added
- xml model encoding api unified with pydantic json encoding api
- root model validation raises exception instead of returning None
- xml model params inheritance implemented
- multiple element search strategies implemented


0.5.0 (2023-01-11)
------------------

- ipaddress objects serialization support added
- py.typed file added
- distutils dependency removed
- default namespace redefinition during serialization fixed (for lxml only). See https://github.com/dapper91/pydantic-xml/issues/27.


0.4.0 (2022-12-19)
------------------

- field default parameter support added.
- field default_factory parameter support added.
- root model validation added.
- pydantic field alias support implemented.


0.3.0 (2022-11-10)
------------------

- recursive (self-referencing) models support added.
- inherit_ns flag dropped due to recursive models implementation details.


0.2.2 (2022-10-07)
------------------

- attribute default namespace bug fixed.


0.2.1 (2022-10-06)
------------------

- default namespace support added.


0.2.0 (2022-08-19)
------------------

- generic models support
- namespace inheritance bug fixed.


0.1.0 (2022-08-17)
------------------

- Initial release
