from . import config

if config.FORCE_STD_XML:
    import xml.etree.ElementTree as etree
else:
    try:
        from lxml import etree  # type: ignore[no-redef]
    except ImportError:
        import xml.etree.ElementTree as etree  # noqa: F401
