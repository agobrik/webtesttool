"""
Setup script for WebTestool
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="webtestool",
    version="1.0.0",
    author="WebTestool Team",
    author_email="info@webtestool.com",
    description="Comprehensive automated web testing framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/webtestool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "webtestool=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.txt", "*.md"],
    },
)
