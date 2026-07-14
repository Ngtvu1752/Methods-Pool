from actions.base import ActionParam, BaseAction


_ACTIONS: dict[str, list[BaseAction]] = {}


class UnsupportedActionError(Exception):
    def __init__(self, action_name: str, dataset_type: str):
        super().__init__(
            f"No action '{action_name}' supports {dataset_type}."
        )

class UnsupportedCapabilityError(Exception):
    def __init__(self, action_name: str):
        super().__init__(f"Unsupported action capability: {action_name}")

def register_action(action_cls: type[BaseAction]) -> type[BaseAction]:
    action = action_cls()

    if not action.name:
        raise ValueError(f"{action_cls.__name__} must define action name.")

    if not action.supported_dataset_types:
        raise ValueError(
            f"{action_cls.__name__} must define supported_dataset_types."
        )

    registered_actions = _ACTIONS.setdefault(action.name, [])

    for registered_action in registered_actions:
        overlap = set(registered_action.supported_dataset_types) & set(
            action.supported_dataset_types
        )
        if overlap:
            dataset_names = ", ".join(t.__name__ for t in overlap)
            raise ValueError(
                f"Action '{action.name}' for {dataset_names} is already "
                f"registered by {registered_action.__class__.__name__}."
            )

    registered_actions.append(action)
    return action_cls


class ActionRegistry:
    @staticmethod
    def get(action_name: str, dataset) -> BaseAction:
        actions = _ACTIONS.get(action_name, [])

        for action in actions:
            if action.can_execute(dataset):
                return action

        raise UnsupportedActionError(
            action_name=action_name,
            dataset_type=type(dataset).__name__,
        )

    @staticmethod
    def all_action_names() -> list[str]:
        return sorted(_ACTIONS.keys())

    @staticmethod
    def describe(action_name: str) -> tuple[str, tuple[ActionParam, ...]]:
        actions = _ACTIONS.get(action_name, [])

        if not actions:
            raise UnsupportedCapabilityError(action_name)

        action = actions[0]
        return action.description, action.params

    @staticmethod
    def all_actions() -> dict[str, tuple[BaseAction, ...]]:
        return {
            name: tuple(actions)
            for name, actions in _ACTIONS.items()
        }

    @staticmethod
    def list_methods() -> list[dict]:
        return [
            ActionRegistry.inspect_method(action_name)
            for action_name in ActionRegistry.all_action_names()
        ]

    @staticmethod
    def search_methods(query: str) -> list[dict]:
        query_lower = query.strip().lower()

        if not query_lower:
            return ActionRegistry.list_methods()

        results = []
        for method in ActionRegistry.list_methods():
            searchable_text = " ".join(
                [
                    method["name"],
                    method["description"],
                    " ".join(param["name"] for param in method["params"]),
                    " ".join(method["supported_dataset_types"]),
                ]
            ).lower()

            if query_lower in searchable_text:
                results.append(method)

        return results

    @staticmethod
    def inspect_method(action_name: str) -> dict:
        actions = _ACTIONS.get(action_name, [])

        if not actions:
            raise UnsupportedCapabilityError(action_name)

        first_action = actions[0]
        return {
            "name": action_name,
            "description": first_action.description,
            "params": [
                ActionRegistry._serialize_param(param)
                for param in first_action.params
            ],
            "supported_dataset_types": sorted(
                {
                    dataset_type.__name__
                    for action in actions
                    for dataset_type in action.supported_dataset_types
                }
            ),
            "implementations": [
                {
                    "class_name": action.__class__.__name__,
                    "module": action.__class__.__module__,
                    "supported_dataset_types": [
                        dataset_type.__name__
                        for dataset_type in action.supported_dataset_types
                    ],
                }
                for action in actions
            ],
        }

    @staticmethod
    def _serialize_param(param: ActionParam) -> dict:
        return {
            "name": param.name,
            "type": getattr(param.type, "__name__", str(param.type)),
            "default": param.default,
            "required": param.default is None,
            "description": param.description,
        }
