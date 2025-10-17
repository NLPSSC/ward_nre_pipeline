class ProcessorNotAvailable(Exception):
    def __init__(self, processor) -> None:
        super().__init__(f"Processor {processor} is not available for processing.")
