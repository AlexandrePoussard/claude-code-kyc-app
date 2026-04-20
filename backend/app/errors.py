"""Domain-level exceptions. API layer maps these to HTTP responses."""


class ApplicationNotFound(Exception):
    def __init__(self, app_id: str):
        super().__init__(f"Application {app_id} not found")
        self.app_id = app_id


class ApplicationAlreadyDecided(Exception):
    def __init__(self, app_id: str):
        super().__init__(f"Application {app_id} has already been decided")
        self.app_id = app_id


class StageNotReachable(Exception):
    """Raised when an action targets a stage the application is not yet in."""

    def __init__(self, app_id: str, required_stage: str, current_stage: str):
        super().__init__(
            f"Application {app_id} is at stage '{current_stage}', action requires '{required_stage}'"
        )
        self.app_id = app_id
        self.required_stage = required_stage
        self.current_stage = current_stage


class RelationshipManagerNotFound(Exception):
    def __init__(self, manager_id: str):
        super().__init__(f"Relationship manager {manager_id} not found")
        self.manager_id = manager_id
