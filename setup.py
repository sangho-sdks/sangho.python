from setuptools import find_packages, setup

setup(
    name="sangho",
    version="0.1.3",
    description="Sangho Python SDK — XAF-first payment platform for Africa",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sangho",
    author_email="nels.holy.allg@gmail.com",
    url="https://github.com/sangho-sdks/sangho.python",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.12",
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
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
