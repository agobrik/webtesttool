"""
GraphQL Testing Module
Tests GraphQL endpoints for security and functionality
"""

import httpx
from typing import Dict
from loguru import logger

from core.models import TestResult, Finding, Severity, Category


class GraphQLTester:
    """GraphQL API Tester"""

    def __init__(self, config):
        self.config = config
        self.timeout = 30

    async def test_graphql_endpoint(self, url: str, test_result: TestResult) -> None:
        """
        Test GraphQL endpoint

        Args:
            url: GraphQL endpoint URL
            test_result: TestResult to add findings to
        """
        # Test introspection
        await self._test_introspection(url, test_result)

        # Test queries
        await self._test_queries(url, test_result)

        # Test mutations
        await self._test_mutations(url, test_result)

        # Test for common vulnerabilities
        await self._test_vulnerabilities(url, test_result)

    async def _test_introspection(self, url: str, test_result: TestResult) -> None:
        """Test GraphQL introspection"""

        introspection_query = '''
        {
            __schema {
                types {
                    name
                    fields {
                        name
                    }
                }
            }
        }
        '''

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(
                    url,
                    json={'query': introspection_query},
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    data = response.json()

                    if 'data' in data and '__schema' in data['data']:
                        # Introspection is enabled
                        test_result.add_finding(Finding(
                            title="GraphQL Introspection Enabled",
                            description="GraphQL introspection is enabled, exposing the entire schema. "
                                      "This can leak sensitive information about the API structure.",
                            severity=Severity.MEDIUM,
                            category=Category.API,
                            url=url,
                            cwe_id="CWE-209",
                            recommendations=[
                                {
                                    'title': 'Disable Introspection in Production',
                                    'description': 'Disable GraphQL introspection in production environments',
                                    'references': ['https://www.apollographql.com/blog/graphql/security/why-you-should-disable-graphql-introspection-in-production/']
                                }
                            ]
                        ))

                        # Analyze schema for sensitive fields
                        await self._analyze_schema(data['data']['__schema'], test_result, url)

        except Exception as e:
            logger.debug(f"GraphQL introspection test error: {str(e)}")

    async def _analyze_schema(self, schema: Dict, test_result: TestResult, url: str) -> None:
        """Analyze GraphQL schema for security issues"""

        sensitive_field_names = ['password', 'secret', 'token', 'api_key', 'private_key', 'ssn', 'credit_card']

        types = schema.get('types', [])

        for type_def in types:
            if type_def.get('fields'):
                for field in type_def['fields']:
                    field_name = field.get('name', '').lower()

                    # Check for sensitive field names
                    if any(sensitive in field_name for sensitive in sensitive_field_names):
                        test_result.add_finding(Finding(
                            title="Potentially Sensitive Field in GraphQL Schema",
                            description=f"GraphQL schema exposes potentially sensitive field: {type_def.get('name')}.{field.get('name')}",
                            severity=Severity.INFO,
                            category=Category.API,
                            url=url
                        ))

    async def _test_queries(self, url: str, test_result: TestResult) -> None:
        """Test GraphQL queries"""

        # Test basic query
        basic_query = '''
        {
            __typename
        }
        '''

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(
                    url,
                    json={'query': basic_query},
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code != 200:
                    logger.debug(f"GraphQL query test failed with status {response.status_code}")

                # Test query depth (DoS vulnerability)
                await self._test_query_depth(client, url, test_result)

        except Exception as e:
            logger.debug(f"GraphQL query test error: {str(e)}")

    async def _test_query_depth(self, client: httpx.AsyncClient, url: str, test_result: TestResult) -> None:
        """Test for query depth attacks"""

        # Create deeply nested query
        deep_query = '''
        {
            level1 {
                level2 {
                    level3 {
                        level4 {
                            level5 {
                                level6 {
                                    level7 {
                                        level8 {
                                            level9 {
                                                level10 {
                                                    __typename
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        '''

        try:
            response = await client.post(
                url,
                json={'query': deep_query},
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                # Query was not blocked - potential DoS vulnerability
                test_result.add_finding(Finding(
                    title="GraphQL Query Depth Not Limited",
                    description="GraphQL endpoint does not limit query depth, potentially vulnerable to DoS attacks",
                    severity=Severity.MEDIUM,
                    category=Category.API,
                    url=url,
                    cwe_id="CWE-400"
                ))

        except Exception as e:
            logger.debug(f"Query depth test error: {str(e)}")

    async def _test_mutations(self, url: str, test_result: TestResult) -> None:
        """Test GraphQL mutations"""

        # Try a generic mutation
        mutation = '''
        mutation {
            __typename
        }
        '''

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(
                    url,
                    json={'query': mutation},
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    logger.debug("GraphQL mutations endpoint responding")

        except Exception as e:
            logger.debug(f"GraphQL mutation test error: {str(e)}")

    async def _test_vulnerabilities(self, url: str, test_result: TestResult) -> None:
        """Test for common GraphQL vulnerabilities"""

        # Test for batch query attacks
        await self._test_batch_queries(url, test_result)

        # Test for field duplication attacks
        await self._test_field_duplication(url, test_result)

        # Test for circular query attacks
        await self._test_circular_queries(url, test_result)

    async def _test_batch_queries(self, url: str, test_result: TestResult) -> None:
        """Test for batch query attacks"""

        # Create batch of queries
        batch_queries = [
            {'query': '{ __typename }'}
            for _ in range(100)
        ]

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(
                    url,
                    json=batch_queries,
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    test_result.add_finding(Finding(
                        title="GraphQL Batch Query Attack Possible",
                        description="GraphQL endpoint accepts batch queries without limit, vulnerable to DoS",
                        severity=Severity.MEDIUM,
                        category=Category.API,
                        url=url
                    ))

        except Exception as e:
            logger.debug(f"Batch query test error: {str(e)}")

    async def _test_field_duplication(self, url: str, test_result: TestResult) -> None:
        """Test for field duplication attacks"""

        # Create query with many duplicate fields
        duplicate_query = '''
        {
            ''' + '\n'.join([f'field{i}: __typename' for i in range(100)]) + '''
        }
        '''

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(
                    url,
                    json={'query': duplicate_query},
                    headers={'Content-Type': 'application/json'}
                )

                if response.status_code == 200:
                    test_result.add_finding(Finding(
                        title="GraphQL Field Duplication Not Limited",
                        description="GraphQL endpoint does not limit field duplication",
                        severity=Severity.LOW,
                        category=Category.API,
                        url=url
                    ))

        except Exception as e:
            logger.debug(f"Field duplication test error: {str(e)}")

    async def _test_circular_queries(self, url: str, test_result: TestResult) -> None:
        """Test for circular query attacks"""

        # This would require knowing the schema structure
        # For now, just log that we attempted it
        logger.debug("Circular query test requires schema knowledge")
