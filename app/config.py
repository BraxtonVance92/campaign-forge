"""Environment-driven configuration. Reads variable NAMES only -- never
hardcodes or logs a secret VALUE. See .env.example for the full list."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gmi_api_key: str | None
    b2_key_id: str | None
    b2_application_key: str | None
    b2_bucket_name: str | None
    b2_endpoint: str | None

    @property
    def gmi_configured(self) -> bool:
        return bool(self.gmi_api_key)

    @property
    def b2_configured(self) -> bool:
        return bool(
            self.b2_key_id
            and self.b2_application_key
            and self.b2_bucket_name
            and self.b2_endpoint
        )


def load_settings() -> Settings:
    return Settings(
        gmi_api_key=os.environ.get("GMI_API_KEY"),
        b2_key_id=os.environ.get("B2_KEY_ID"),
        b2_application_key=os.environ.get("B2_APPLICATION_KEY"),
        b2_bucket_name=os.environ.get("B2_BUCKET_NAME"),
        b2_endpoint=os.environ.get("B2_ENDPOINT"),
    )
