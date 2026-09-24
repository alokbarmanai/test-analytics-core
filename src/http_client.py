import requests


class RemoteTelemetrySyncClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def sync_metrics_payload(self, stream_id: str, average_metric: float) -> bool:
        target_endpoint = f"{self.base_url}/v1/telemetry"
        payload = {"id": stream_id, "avg_value": average_metric}

        try:
            # Dispatch outbound network call to external data engine
            response = requests.post(target_endpoint, json=payload, timeout=5.0)

            # If server drops an error code (4xx or 5xx), this raises an HTTPError
            response.raise_for_status()

            data = response.json()
            return data.get("synced") == True

        except requests.RequestException:
            # Gracefully handle network timeouts or server crashes
            return False
