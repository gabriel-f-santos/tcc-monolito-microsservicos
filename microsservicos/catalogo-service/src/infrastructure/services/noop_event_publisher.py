from src.domain.services.event_publisher import EventPublisher


class NoopEventPublisher(EventPublisher):
    def publish(self, event_type: str, payload: dict) -> None:
        pass
