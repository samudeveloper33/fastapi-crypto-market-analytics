from typing import Dict, List

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CoinGeckoClient:
    def __init__(self):
        self.api_url = settings.coingecko_api_url
        self.api_key = settings.coingecko_api_key
        self.timeout = settings.coingecko_timeout
    
    async def fetch_top_cryptos(self, limit: int = 10) -> List[Dict]:
        headers = {}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": limit,
                        "page": 1,
                        "sparkline": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Fetched {len(data)} cryptocurrencies from CoinGecko")
                return data
                
            except httpx.HTTPError as e:
                logger.error(f"CoinGecko API error: {e}")
                raise
