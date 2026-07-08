from actions.base import BaseAction


_ACTIONS: dict[str, list[BaseAction]] = {}


class UnsupportedActionError(Exception):
    def __init__(self, action_name: str, dataset_type: str):
        super().__init__(
            f"No action '{action_name}' supports {dataset_type}."
        )


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
    def all_actions() -> dict[str, tuple[BaseAction, ...]]:
        return {
            name: tuple(actions)
            for name, actions in _ACTIONS.items()
        }