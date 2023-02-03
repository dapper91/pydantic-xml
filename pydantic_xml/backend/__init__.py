from pydantic_xml import config

if config.FORCE_STD_XML:
    from .std import *  # noqa: F403
else:
    try:
        from .lxml import *  # type: ignore[no-redef]  # noqa: F403
    except ImportError:
        from .std import *  # noqa: F403