from typing import Callable, Optional, Tuple, Union

from mypy import nodes
from mypy.plugin import ClassDefContext, Plugin
from pydantic.mypy import PydanticModelTransformer, PydanticPlugin

MODEL_METACLASS_FULLNAME = 'pydantic_xml.model.XmlModelMeta'
ATTR_FULLNAME = 'pydantic_xml.model.attr'
ELEMENT_FULLNAME = 'pydantic_xml.model.element'
WRAPPED_FULLNAME = 'pydantic_xml.model.wrapped'
ENTITIES_FULLNAME = (ATTR_FULLNAME, ELEMENT_FULLNAME, WRAPPED_FULLNAME)


def plugin(version: str) -> type[Plugin]:
    return PydanticXmlPlugin


class PydanticXmlPlugin(PydanticPlugin):
    def get_metaclass_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname == MODEL_METACLASS_FULLNAME:
            return self._pydantic_model_metaclass_marker_callback
        return super().get_metaclass_hook(fullname)

    def _pydantic_model_class_maker_callback(self, ctx: ClassDefContext) -> None:
        transformer = PydanticXmlModelTransformer(ctx.cls, ctx.reason, ctx.api, self.plugin_config)
        transformer.transform()


class PydanticXmlModelTransformer(PydanticModelTransformer):
    @staticmethod
    def get_has_default(stmt: nodes.AssignmentStmt) -> bool:
        expr = stmt.rvalue
        if isinstance(expr, nodes.TempNode):
            return False

        if (
            isinstance(expr, nodes.CallExpr) and
            isinstance(expr.callee, nodes.RefExpr) and
            expr.callee.fullname in ENTITIES_FULLNAME
        ):
            for arg, name in zip(expr.args, expr.arg_names):
                if name == 'default':
                    return arg.__class__ is not nodes.EllipsisExpr
                if name == 'default_factory':
                    return not (isinstance(arg, nodes.NameExpr) and arg.fullname == 'builtins.None')

            return False

        return PydanticModelTransformer.get_has_default(stmt)

    @staticmethod
    def get_alias_info(stmt: nodes.AssignmentStmt) -> Tuple[Union[str, None], bool]:
        expr = stmt.rvalue
        if isinstance(expr, nodes.TempNode):
            return None, False

        if (
            isinstance(expr, nodes.CallExpr) and
            isinstance(expr.callee, nodes.RefExpr) and
            expr.callee.fullname in ENTITIES_FULLNAME
        ):
            for arg, arg_name in zip(expr.args, expr.arg_names):
                if arg_name != 'alias':
                    continue
                if isinstance(arg, nodes.StrExpr):
                    return arg.value, False
                else:
                    return None, True

        return PydanticModelTransformer.get_alias_info(stmt)

    @staticmethod
    def get_strict(stmt: nodes.AssignmentStmt) -> Optional[bool]:
        expr = stmt.rvalue
        if (
            isinstance(expr, nodes.CallExpr) and
            isinstance(expr.callee, nodes.RefExpr) and
            expr.callee.fullname in ENTITIES_FULLNAME
        ):
            for arg, name in zip(expr.args, expr.arg_names):
                if name != 'strict':
                    continue
                if isinstance(arg, nodes.NameExpr):
                    if arg.fullname == 'builtins.True':
                        return True
                    elif arg.fullname == 'builtins.False':
                        return False
                return None

        return PydanticModelTransformer.get_strict(stmt)

    @staticmethod
    def is_field_frozen(stmt: nodes.AssignmentStmt) -> bool:
        expr = stmt.rvalue
        if isinstance(expr, nodes.TempNode):
            return False

        if not (
            isinstance(expr, nodes.CallExpr) and
            isinstance(expr.callee, nodes.RefExpr) and
            expr.callee.fullname in ENTITIES_FULLNAME
        ):
            return False

        for i, arg_name in enumerate(expr.arg_names):
            if arg_name == 'frozen':
                arg = expr.args[i]
                return isinstance(arg, nodes.NameExpr) and arg.fullname == 'builtins.True'

        return PydanticModelTransformer.is_field_frozen(stmt)
