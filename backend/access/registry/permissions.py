from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionDefinition:
    resource: str
    action: str
    name: str
    description: str = ""

    @property
    def code(self):
        return f"{self.resource}.{self.action}"


class PermissionRegistry:
    def __init__(self):
        self._permissions = {}

    def register(self, *, resource, permissions):
        if not isinstance(resource, str) or not resource.strip():
            raise ValueError("Permission resource must be a non-empty string.")

        resource = resource.strip()

        for action, name in permissions.items():
            if not isinstance(action, str) or not action.strip():
                raise ValueError(
                    f"Permission action for resource '{resource}' "
                    "must be a non-empty string."
                )

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    f"Permission name for '{resource}.{action}' "
                    "must be a non-empty string."
                )

            action = action.strip()
            name = name.strip()

            permission = PermissionDefinition(
                resource=resource,
                action=action,
                name=name,
            )

            if permission.code in self._permissions:
                raise ValueError(
                    f"Permission '{permission.code}' is already registered."
                )

            self._permissions[permission.code] = permission

    def all(self):
        return tuple(self._permissions.values())

    def get(self, code):
        return self._permissions.get(code)

    def clear(self):
        self._permissions.clear()


registry = PermissionRegistry()


def register_permissions(*, resource, permissions):
    registry.register(
        resource=resource,
        permissions=permissions,
    )