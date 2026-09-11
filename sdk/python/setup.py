from setuptools import setup, find_packages

setup(
    name="greenagent-sdk",
    version="1.0.0",
    description="Python Client SDK for GreenAgent OS Carbon & Energy Optimization",
    author="Vijay Mahes",
    author_email="Vijaypradhap2004@gmail.com",
    packages=find_packages(),
    install_requires=["httpx>=0.24.0", "pydantic>=2.0.0"],
    python_requires=">=3.8",
)
