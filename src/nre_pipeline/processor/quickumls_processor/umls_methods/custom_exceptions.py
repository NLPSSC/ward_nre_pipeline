class EarlyTerminationError(Exception):
    """Exception raised when a process is terminated early."""

    def __init__(self, response):
        self.response = response
        super().__init__(f"Process terminated early: {response.status_code}")
