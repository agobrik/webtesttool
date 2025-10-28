"""SEO Testing Module"""

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from core.module_loader import BaseTestModule
from core.models import Category, ModuleResult, TestResult, TestStatus, Finding, Severity, TestContext


class SEOModule(BaseTestModule):
    """SEO Testing Module"""

    name = "seo"
    description = "SEO testing including meta tags, structured data, and best practices"
    category = Category.SEO
    version = "1.0.0"

    async def run(self, context: TestContext) -> ModuleResult:
        module_result = ModuleResult(name=self.name, category=self.category, status=TestStatus.RUNNING)

        test_result = TestResult(name="seo_analysis", description="SEO best practices check",
                                category=self.category, status=TestStatus.RUNNING)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(context.target_url)
                soup = BeautifulSoup(response.text, 'lxml')

                # Title check
                title = soup.find('title')
                if not title or not title.string:
                    test_result.add_finding(Finding(
                        title="Missing Title Tag", description="Page is missing a title tag",
                        severity=Severity.HIGH, category=self.category, url=context.target_url, cwe_id="SEO-001"
                    ))
                elif len(title.string) > 60:
                    test_result.add_finding(Finding(
                        title="Title Too Long", description=f"Title is {len(title.string)} chars (recommended <60)",
                        severity=Severity.LOW, category=self.category, url=context.target_url
                    ))

                # Meta description
                meta_desc = soup.find('meta', {'name': 'description'})
                if not meta_desc or not meta_desc.get('content'):
                    test_result.add_finding(Finding(
                        title="Missing Meta Description", description="Page lacks meta description",
                        severity=Severity.MEDIUM, category=self.category, url=context.target_url
                    ))

                # Meta viewport (mobile-friendly)
                viewport = soup.find('meta', {'name': 'viewport'})
                if not viewport:
                    test_result.add_finding(Finding(
                        title="Missing Viewport Meta Tag", description="Page not optimized for mobile",
                        severity=Severity.MEDIUM, category=self.category, url=context.target_url
                    ))

                # Heading structure
                h1_tags = soup.find_all('h1')
                if not h1_tags:
                    test_result.add_finding(Finding(
                        title="Missing H1 Tag", description="Page has no H1 heading",
                        severity=Severity.MEDIUM, category=self.category, url=context.target_url
                    ))
                elif len(h1_tags) > 1:
                    test_result.add_finding(Finding(
                        title="Multiple H1 Tags", description=f"Page has {len(h1_tags)} H1 tags (recommended: 1)",
                        severity=Severity.LOW, category=self.category, url=context.target_url
                    ))

                # Images without alt text
                images = soup.find_all('img')
                images_without_alt = [img for img in images if not img.get('alt')]
                if images_without_alt:
                    test_result.add_finding(Finding(
                        title="Images Missing Alt Text",
                        description=f"{len(images_without_alt)} images missing alt attributes",
                        severity=Severity.MEDIUM, category=self.category, url=context.target_url
                    ))

                # Canonical URL
                canonical = soup.find('link', {'rel': 'canonical'})
                if not canonical:
                    test_result.add_finding(Finding(
                        title="Missing Canonical URL", description="No canonical link tag found",
                        severity=Severity.LOW, category=self.category, url=context.target_url
                    ))

                # Open Graph tags
                og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
                if not og_tags:
                    test_result.add_finding(Finding(
                        title="Missing Open Graph Tags", description="No OG tags for social sharing",
                        severity=Severity.LOW, category=self.category, url=context.target_url
                    ))

                # Structured data (schema.org)
                schema_scripts = soup.find_all('script', {'type': 'application/ld+json'})
                if not schema_scripts:
                    test_result.add_finding(Finding(
                        title="No Structured Data", description="No Schema.org structured data found",
                        severity=Severity.LOW, category=self.category, url=context.target_url
                    ))

                # Robots meta tag
                robots_meta = soup.find('meta', {'name': 'robots'})
                if robots_meta and 'noindex' in robots_meta.get('content', '').lower():
                    test_result.add_finding(Finding(
                        title="Page Set to No-Index", description="Page blocked from search engines",
                        severity=Severity.INFO, category=self.category, url=context.target_url
                    ))

        except Exception as e:
            logger.error(f"SEO test error: {str(e)}")

        test_result.mark_completed(TestStatus.PASSED)
        module_result.add_test_result(test_result)
        module_result.mark_completed(TestStatus.PASSED)
        return module_result
