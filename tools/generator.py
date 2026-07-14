import inspect
from collections.abc import Callable
from typing import Any

from actions.registry import ActionRegistry


def _build_tool(action_name: str, hub) -> Callable[..., Any]:
    description, params = ActionRegistry.describe(action_name)
    signature_params = [
        inspect.Parameter(
            "dataset_id",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=str,
        )
    ]

    for param in params:
        signature_params.append(
            inspect.Parameter(
                param.name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=param.type,
                default=param.default,
            )
        )

    async def tool_func(**kwargs: Any) -> dict[str, Any]:
        dataset_id = kwargs.pop("dataset_id")
        return await hub.execute_action(action_name, dataset_id, **kwargs)

    tool_func.__name__ = action_name
    tool_func.__doc__ = description
    tool_func.__signature__ = inspect.Signature(signature_params)
    return tool_func


def build_all_tools(hub) -> list[Callable[..., Any]]:
    """Build one FastMCP-compatible function for each registered action name."""
    return [
        _build_tool(action_name, hub)
        for action_name in ActionRegistry.all_action_names()
    ]
