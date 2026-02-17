import httpx
from azure.identity.aio import ClientSecretCredential
from typing import Any
import structlog

logger = structlog.get_logger()


class AzureClient:
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.arm_endpoint = "https://management.azure.com"
        self.api_version = "2023-11-01"
        self.metrics_api_version = "2023-10-01"

    async def close(self):
        await self.http_client.aclose()

    async def get_token(self, tenant_id: str, client_id: str, client_secret: str) -> str:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        token = await credential.get_token("https://management.azure.com/.default")
        await credential.close()
        return token.token

    async def list_capacities(
        self, token: str, subscription_id: str, resource_group: str | None = None
    ) -> list[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {token}"}
        
        if resource_group:
            url = (
                f"{self.arm_endpoint}/subscriptions/{subscription_id}"
                f"/resourceGroups/{resource_group}"
                f"/providers/Microsoft.Fabric/capacities"
                f"?api-version={self.api_version}"
            )
        else:
            url = (
                f"{self.arm_endpoint}/subscriptions/{subscription_id}"
                f"/providers/Microsoft.Fabric/capacities"
                f"?api-version={self.api_version}"
            )

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            capacities_body = response.json()
            return capacities_body.get("value", [])
        except httpx.HTTPStatusError as e:
            logger.error(
                "arm_api_error",
                url=url,
                status_code=e.response.status_code,
                response=e.response.text,
            )
            raise
        except Exception as e:
            logger.error("arm_api_exception", url=url, error=str(e))
            raise

    async def get_capacity(self, token: str, resource_id: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.arm_endpoint}{resource_id}?api-version={self.api_version}"

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "get_capacity_error",
                resource_id=resource_id,
                status_code=e.response.status_code,
                response=e.response.text,
            )
            raise
        except Exception as e:
            logger.error("get_capacity_exception", resource_id=resource_id, error=str(e))
            raise

    async def get_metric_definitions(self, token: str, resource_id: str) -> list[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {token}"}
        url = (
            f"{self.arm_endpoint}{resource_id}"
            f"/providers/Microsoft.Insights/metricDefinitions"
            f"?api-version={self.metrics_api_version}"
        )

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            definitions_body = response.json()
            return definitions_body.get("value", [])
        except httpx.HTTPStatusError as e:
            logger.warning(
                "metric_definitions_not_available",
                resource_id=resource_id,
                status_code=e.response.status_code,
            )
            return []
        except Exception as e:
            logger.warning("metric_definitions_exception", resource_id=resource_id, error=str(e))
            return []

    async def get_metrics(
        self,
        token: str,
        resource_id: str,
        metric_names: list[str],
        timespan: str,
        interval: str = "PT5M",
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}
        metricnames = ",".join(metric_names)
        url = (
            f"{self.arm_endpoint}{resource_id}"
            f"/providers/Microsoft.Insights/metrics"
            f"?api-version={self.metrics_api_version}"
            f"&metricnames={metricnames}"
            f"&timespan={timespan}"
            f"&interval={interval}"
        )

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "metrics_not_available",
                resource_id=resource_id,
                status_code=e.response.status_code,
            )
            return {"value": []}
        except Exception as e:
            logger.warning("metrics_exception", resource_id=resource_id, error=str(e))
            return {"value": []}
