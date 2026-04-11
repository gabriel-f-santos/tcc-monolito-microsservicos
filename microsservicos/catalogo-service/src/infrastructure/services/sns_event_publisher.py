import json
import os

import boto3

from src.domain.services.event_publisher import EventPublisher


class SnsEventPublisher(EventPublisher):
    def __init__(self) -> None:
        self._client = boto3.client("sns")
        self._topic_arn = os.environ["EVENTOS_TOPIC_ARN"]

    def publish(self, event_type: str, payload: dict) -> None:
        self._client.publish(
            TopicArn=self._topic_arn,
            Message=json.dumps(payload),
            MessageAttributes={
                "event_type": {
                    "DataType": "String",
                    "StringValue": event_type,
                }
            },
        )
