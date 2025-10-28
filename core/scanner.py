"""
Web Scanner - Crawls and discovers website structure
"""

import asyncio
import re
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import httpx
from loguru import logger

from .models import CrawledPage, ApiEndpoint
from .config import ConfigManager
from utils.cache_manager import CacheManager


class WebScanner:
    """
    Web Scanner
    Crawls website to discover pages, forms, API endpoints, and structure
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize WebScanner

        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.crawled_urls: Set[str] = set()
        self.crawled_pages: List[CrawledPage] = []
        self.api_endpoints: List[ApiEndpoint] = []
        self.base_url = config.config.target.url
        self.max_depth = config.config.crawler.max_depth
        self.max_pages = config.config.crawler.max_pages
        self.timeout = config.config.crawler.timeout
        self.concurrent_requests = config.config.crawler.concurrent_requests
        self.crawl_delay = config.config.crawler.crawl_delay
        self.follow_external = config.config.crawler.follow_external
        self.exclude_patterns = config.config.crawler.exclude_patterns
        self.include_patterns = config.config.crawler.include_patterns

        # Headers and cookies from config
        self.headers = config.config.target.headers
        self.cookies = config.config.target.cookies

        # Semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(self.concurrent_requests)

        # Initialize cache manager
        cache_config = config.config.cache if hasattr(config.config, 'cache') else None

        # Helper function to get value from dict or object
        def get_value(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        cache_enabled = get_value(cache_config, 'enabled', False) if cache_config else False

        if cache_enabled:
            redis_config = get_value(cache_config, 'redis', {})
            disk_config = get_value(cache_config, 'disk', {})
            memory_config = get_value(cache_config, 'memory', {})

            redis_enabled = get_value(redis_config, 'enabled', False)
            redis_url = get_value(redis_config, 'url') if redis_enabled else None
            cache_dir = get_value(disk_config, 'directory', '.cache') if get_value(disk_config, 'enabled', False) else ".cache"
            memory_max_size = get_value(memory_config, 'max_size', 1000)
            default_ttl = get_value(memory_config, 'ttl', 3600)

            self.cache = CacheManager(
                redis_url=redis_url,
                cache_dir=cache_dir,
                memory_max_size=memory_max_size,
                default_ttl=default_ttl,
                enable_redis=redis_enabled
            )
            self.cache_enabled = True
            logger.info("Cache manager initialized for scanner")
        else:
            self.cache = None
            self.cache_enabled = False
            logger.info("Cache disabled for scanner")

    async def scan(self) -> tuple[List[CrawledPage], List[ApiEndpoint]]:
        """
        Start the web scanning process

        Returns:
            Tuple of (crawled_pages, api_endpoints)
        """
        logger.info(f"Starting web scan for {self.base_url}")

        # Connect to cache
        if self.cache_enabled:
            await self.cache.connect()
            logger.info("Cache connected")

        # Start crawling from base URL
        await self._crawl_url(self.base_url, depth=0)

        logger.info(f"Scan completed. Crawled {len(self.crawled_pages)} pages, "
                    f"discovered {len(self.api_endpoints)} API endpoints")

        # Log cache statistics
        if self.cache_enabled:
            stats = self.cache.get_stats()
            logger.info(f"Cache statistics: {stats}")
            hit_rate = stats.get('hit_rate', 0)
            logger.info(f"Cache hit rate: {hit_rate:.2%}")

        return self.crawled_pages, self.api_endpoints

    async def _crawl_url(self, url: str, depth: int = 0, parent_url: Optional[str] = None) -> None:
        """
        Crawl a single URL

        Args:
            url: URL to crawl
            depth: Current depth level
            parent_url: Parent URL that linked to this URL
        """
        # Check if we should crawl this URL
        if not self._should_crawl(url, depth):
            return

        # Mark as crawled
        self.crawled_urls.add(url)

        # Rate limiting
        async with self.semaphore:
            try:
                # Add delay
                if self.crawl_delay > 0:
                    await asyncio.sleep(self.crawl_delay)

                # Check cache first
                cached_response = None
                if self.cache_enabled:
                    cached_response = await self.cache.get(url)
                    if cached_response:
                        logger.debug(f"Cache HIT: {url}")

                # Process cached data or fetch fresh
                page = None
                if cached_response:
                    # Use cached response
                    response_data = cached_response
                    response_time = 0  # Cached, no network time

                    # Create crawled page object from cache
                    # If cached data is dict, deserialize to CrawledPage
                    if isinstance(response_data, dict):
                        page = CrawledPage(**response_data)
                    elif isinstance(response_data, CrawledPage):
                        page = response_data
                    else:
                        # Invalid cache data, fetch fresh
                        logger.warning(f"Invalid cache data type for {url}: {type(response_data)}")
                        page = None

                if not page:
                    # Fetch from network
                    async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                        import time
                        start_time = time.time()

                        response = await client.get(
                            url,
                            headers=self.headers,
                            cookies=self.cookies
                        )

                        response_time = time.time() - start_time
                        logger.debug(f"Cache MISS: {url} (fetched in {response_time:.2f}s)")

                        # Create crawled page object
                        page = await self._parse_response(
                            url, response, depth, parent_url, response_time
                        )

                        # Store in cache
                        if page and self.cache_enabled:
                            await self.cache.set(url, page)

                if page:
                    self.crawled_pages.append(page)
                    logger.debug(f"Crawled: {url} (depth: {depth})")

                    # Extract and crawl links if not at max depth
                    if depth < self.max_depth and page.links:
                        tasks = []
                        for link in page.links:
                            if len(self.crawled_urls) < self.max_pages:
                                tasks.append(self._crawl_url(link, depth + 1, url))

                        # Crawl links concurrently
                        if tasks:
                            await asyncio.gather(*tasks, return_exceptions=True)

            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")

    def _should_crawl(self, url: str, depth: int) -> bool:
        """
        Determine if a URL should be crawled

        Args:
            url: URL to check
            depth: Current depth

        Returns:
            True if should crawl, False otherwise
        """
        # Already crawled
        if url in self.crawled_urls:
            return False

        # Max pages reached
        if len(self.crawled_urls) >= self.max_pages:
            return False

        # Max depth reached
        if depth > self.max_depth:
            return False

        # Parse URL
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)

        # External link check
        if not self.follow_external:
            if parsed.netloc != base_parsed.netloc:
                return False

        # Exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, url):
                logger.debug(f"Excluding {url} (matches pattern: {pattern})")
                return False

        # Include patterns (if specified, URL must match at least one)
        if self.include_patterns:
            matched = False
            for pattern in self.include_patterns:
                if re.search(pattern, url):
                    matched = True
                    break
            if not matched:
                return False

        return True

    async def _parse_response(
        self,
        url: str,
        response: httpx.Response,
        depth: int,
        parent_url: Optional[str],
        response_time: float
    ) -> Optional[CrawledPage]:
        """
        Parse HTTP response and extract information

        Args:
            url: URL of the response
            response: HTTP response object
            depth: Crawl depth
            parent_url: Parent URL
            response_time: Response time in seconds

        Returns:
            CrawledPage object or None
        """
        try:
            content_type = response.headers.get('content-type', '').lower()

            # Only parse HTML pages
            if 'html' not in content_type:
                # Check if it's an API endpoint
                if 'json' in content_type or 'xml' in content_type:
                    self._discover_api_endpoint(url, response)
                return None

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract title
            title = soup.title.string if soup.title else None

            # Extract meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    meta_tags[name] = content

            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                # Remove fragment
                link = link.split('#')[0]
                if link not in links:
                    links.append(link)

            # Extract forms
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    'action': urljoin(url, form.get('action', '')),
                    'method': form.get('method', 'get').upper(),
                    'inputs': []
                }

                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'name': input_tag.get('name'),
                        'type': input_tag.get('type', 'text'),
                        'value': input_tag.get('value'),
                        'required': input_tag.has_attr('required')
                    }
                    form_data['inputs'].append(input_data)

                forms.append(form_data)

            # Extract all inputs (including outside forms)
            inputs = []
            for input_tag in soup.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': input_tag.get('name'),
                    'type': input_tag.get('type', 'text'),
                    'id': input_tag.get('id'),
                    'value': input_tag.get('value'),
                }
                inputs.append(input_data)

            # Extract scripts
            scripts = []
            for script in soup.find_all('script', src=True):
                scripts.append(urljoin(url, script['src']))

            # Extract stylesheets
            stylesheets = []
            for link in soup.find_all('link', rel='stylesheet', href=True):
                stylesheets.append(urljoin(url, link['href']))

            # Extract cookies
            cookies = []
            for cookie_name, cookie_value in response.cookies.items():
                cookies.append({
                    'name': cookie_name,
                    'value': cookie_value
                })

            # Detect potential API endpoints in JavaScript
            self._discover_api_from_js(soup, url)

            # Create CrawledPage object
            page = CrawledPage(
                url=url,
                status_code=response.status_code,
                content_type=content_type,
                title=title,
                depth=depth,
                parent_url=parent_url,
                forms=forms,
                links=links,
                inputs=inputs,
                scripts=scripts,
                stylesheets=stylesheets,
                meta_tags=meta_tags,
                headers=dict(response.headers),
                cookies=cookies,
                response_time=response_time,
                size_bytes=len(response.content)
            )

            return page

        except Exception as e:
            logger.error(f"Error parsing response from {url}: {str(e)}")
            return None

    def _discover_api_endpoint(self, url: str, response: httpx.Response) -> None:
        """
        Discover and record API endpoint

        Args:
            url: Endpoint URL
            response: HTTP response
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        parameters = []
        for key, values in query_params.items():
            parameters.append({
                'name': key,
                'value': values[0] if values else None,
                'location': 'query'
            })

        endpoint = ApiEndpoint(
            url=url,
            method='GET',  # Detected from crawling
            parameters=parameters,
            response_type=response.headers.get('content-type', ''),
            discovered_from='crawler'
        )

        self.api_endpoints.append(endpoint)
        logger.debug(f"Discovered API endpoint: {url}")

    def _discover_api_from_js(self, soup: BeautifulSoup, page_url: str) -> None:
        """
        Discover API endpoints from JavaScript code

        Args:
            soup: BeautifulSoup object
            page_url: Page URL containing the JavaScript
        """
        # Patterns to match API endpoints in JS
        patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.[get|post|put|delete]+\(["\']([^"\']+)["\']',
            r'\$\.ajax\(\{[^}]*url:\s*["\']([^"\']+)["\']',
            r'XMLHttpRequest.*open\(["\']([A-Z]+)["\']\s*,\s*["\']([^"\']+)["\']',
            r'["\']/(api|graphql|rest|v\d+)/[^"\']+["\']',
        ]

        for script in soup.find_all('script'):
            if script.string:
                for pattern in patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            url = match[-1]
                        else:
                            url = match

                        # Make absolute URL
                        absolute_url = urljoin(page_url, url)

                        # Check if not already discovered
                        if not any(e.url == absolute_url for e in self.api_endpoints):
                            endpoint = ApiEndpoint(
                                url=absolute_url,
                                method='UNKNOWN',
                                discovered_from=f'javascript:{page_url}'
                            )
                            self.api_endpoints.append(endpoint)
                            logger.debug(f"Discovered API endpoint from JS: {absolute_url}")

    def get_forms(self) -> List[Dict]:
        """Get all discovered forms"""
        forms = []
        for page in self.crawled_pages:
            forms.extend(page.forms)
        return forms

    def get_inputs(self) -> List[Dict]:
        """Get all discovered inputs"""
        inputs = []
        for page in self.crawled_pages:
            inputs.extend(page.inputs)
        return inputs

    def get_urls_by_pattern(self, pattern: str) -> List[str]:
        """
        Get URLs matching a regex pattern

        Args:
            pattern: Regex pattern

        Returns:
            List of matching URLs
        """
        return [page.url for page in self.crawled_pages if re.search(pattern, page.url)]

    async def close(self) -> None:
        """
        Close scanner and cleanup resources
        """
        if self.cache_enabled and self.cache:
            await self.cache.close()
            logger.info("Cache connection closed")
