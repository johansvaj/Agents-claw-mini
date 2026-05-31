"""Setup script for Agents Claw Mini."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agents-claw-mini",
    version="1.0.0",
    author="Agents Claw Mini Team",
    author_email="team@agents-claw-mini.dev",
    description="A lightweight, modular AI Agent Framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agents-claw-mini",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "all": [
            "selenium>=4.0.0",
            "playwright>=1.40.0",
            "chromadb>=0.4.0",
            "qdrant-client>=1.6.0",
            "redis>=5.0.0",
            "python-telegram-bot>=20.0",
            "discord.py>=2.3.0",
            "slack-sdk>=3.21.0",
        ],
        "browser": ["selenium>=4.0.0", "playwright>=1.40.0"],
        "vector": ["chromadb>=0.4.0", "qdrant-client>=1.6.0"],
        "channels": ["python-telegram-bot>=20.0", "discord.py>=2.3.0", "slack-sdk>=3.21.0"],
    },
    entry_points={
        "console_scripts": [
            "agents-claw-mini=agents_claw_mini.cli:main",
        ],
    },
)
