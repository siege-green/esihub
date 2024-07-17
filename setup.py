import os
import re

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version():
    init_py = open(
        os.path.join(os.path.dirname(__file__), "esihub", "__init__.py")
    ).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version()

setup(
    name="esihub",
    version="0.1.0",
    author="MelonCafe",
    author_email="contact@siege-green.com",
    description="An asynchronous client library for EVE ONLINE ESI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/siege-green/esihub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.8.0",
        "aioredis>=2.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=23.0.0",
            "isort>=5.10.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "esihub": ["py.typed", "swagger.json"],
    },
    project_urls={
        "Bug Tracker": "https://github.com/siege-green/esihub/issues",
        "Documentation": "https://esihub.siege-green.com/",
        "Source Code": "https://github.com/siege-green/esihub",
    },
)
