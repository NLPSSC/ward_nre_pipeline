class NonExistentRouteSegmentException(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Non-existent route segment: {name}")