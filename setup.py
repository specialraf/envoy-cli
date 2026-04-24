"""Setup configuration for envoy-cli."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="envoy-cli",
    version="0.1.0",
    author="envoy-cli contributors",
    description="A smart CLI tool for managing and syncing .env files across projects with encrypted remote storage support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/envoy-cli",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "cryptography>=41.0",
        "requests>=2.28",
        "toml>=0.10",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "responses>=0.23",
        ]
    },
    entry_points={
        "console_scripts": [
            "envoy=envoy.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="dotenv env secrets cli encryption sync",
    project_urls={
        "Bug Reports": "https://github.com/your-org/envoy-cli/issues",
        "Source": "https://github.com/your-org/envoy-cli",
    },
)
