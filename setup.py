from setuptools import setup, find_packages

setup(
    name="sangho",
    version="1.0.0",
    description="Sangho Python SDK — XAF-first payment platform for Africa",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sangho",
    author_email="dev@sangho.com",
    url="https://github.com/sangho/sangho-python",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "pytest-asyncio>=0.23",
            "respx>=0.21",
            "ruff>=0.4",
            "mypy>=1.10",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
