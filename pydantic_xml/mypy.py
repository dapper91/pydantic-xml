from typing import Callable, Optional, Tuple, Union

from mypy import nodes
from mypy.plugin import ClassDefContext, FunctionContext, Plugin, Type
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

    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], Type]]:
        sym = self.lookup_fully_qualified(fullname)
        if sym and sym.fullname == ATTR_FULLNAME:
            return self._attribute_callback
        elif sym and sym.fullname == ELEMENT_FULLNAME:
            return self._element_callback
        elif sym and sym.fullname == WRAPPED_FULLNAME:
            return self._wrapped_callback

        return super().get_function_hook(fullname)

    def _attribute_callback(self, ctx: FunctionContext) -> Type:
        return super()._pydantic_field_callback(self._pop_first_args(ctx, 2))

    def _element_callback(self, ctx: FunctionContext) -> Type:
        return super()._pydantic_field_callback(self._pop_first_args(ctx, 4))

    def _wrapped_callback(self, ctx: FunctionContext) -> Type:
        return super()._pydantic_field_callback(self._pop_first_args(ctx, 4))

    def _pop_first_args(self, ctx: FunctionContext, num: int) -> FunctionContext:
        return FunctionContext(
            arg_types=ctx.arg_types[num:],
            arg_kinds=ctx.arg_kinds[num:],
            callee_arg_names=ctx.callee_arg_names[num:],
            arg_names=ctx.arg_names[num:],
            default_return_type=ctx.default_return_type,
            args=ctx.args[num:],
            context=ctx.context,
            api=ctx.api,
        )

    def _pydantic_model_class_maker_callback(self, ctx: ClassDefContext) -> bool:
        transformer = PydanticXmlModelTransformer(ctx.cls, ctx.reason, ctx.api, self.plugin_config)
        return transformer.transform()


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
