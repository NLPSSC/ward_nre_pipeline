class StandaloneMixin:
    """Mixin class to provide standalone functionality.
    """

    def direct_call(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")