#!/usr/bin/env python3
"""Setup configuration for JobMatch CLI package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="jobmatch-cli",
    version="0.1.0",
    description="Terminal-based capability matching interface for JobMatch.zip paid beta users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="JobMatch.zip Team",
    author_email="contact@jobmatch.zip",
    url="https://github.com/XDM-ZSBW/jobmatch-ai",
    project_urls={
        "Bug Tracker": "https://github.com/XDM-ZSBW/jobmatch-ai/issues",
        "Documentation": "https://github.com/XDM-ZSBW/jobmatch-ai#readme",
        "Source Code": "https://github.com/XDM-ZSBW/jobmatch-ai",
    },
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    py_modules=["jobmatch_cli"],
    entry_points={
        "console_scripts": [
            "jobmatch-cli=jobmatch_cli:main",
        ],
    },
    install_requires=[
        "psycopg2-binary>=2.9.0",
        "redis>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Topic :: Office/Business",
    ],
    keywords="cli capability matching jobmatch ai llm",
)
