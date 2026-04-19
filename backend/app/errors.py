"""Domain-level exceptions. API layer maps these to HTTP responses."""


class ApplicationNotFound(Exception):
    def __init__(self, app_id: str):
        super().__init__(f"Application {app_id} not found")
        self.app_id = app_id


class ApplicationAlreadyDecided(Exception):
    def __init__(self, app_id: str):
        super().__init__(f"Application {app_id} has already been decided")
        self.app_id = app_id
