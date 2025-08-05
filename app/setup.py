"""
Setup script for FAdvisor
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fadvisor",
    version="0.1.0",
    author="FAdvisor Team",
    author_email="",
    description="AI Financial Advisor using Google Agent Development Kit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fadvisor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.10",
    install_requires=[
        "google-adk>=0.1.0",
        "litellm>=1.65.5",
        "python-dotenv>=1.0.0",
        "yfinance>=0.2.18",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "ta>=0.10.2",
        "newsapi-python>=0.2.7",
        "finnhub-python>=2.4.0",
        "aiohttp>=3.9.0",
        "httpx>=0.25.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "fadvisor=app.main:main",
            "fadvisor-api=app.api_server:main",
        ],
    },
)