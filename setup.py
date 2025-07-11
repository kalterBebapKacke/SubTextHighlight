from setuptools import setup, find_packages

setup(
    name="SubTextHighlight",
    version="0.1.1",
    author="N01d3a",
    description="This is a Package for generating and formatting subtitles while focusing on user-friendliness and providing many features.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pysubs2>=1.8.0",
        "Cython>=3.1.1",
        "openai-whisper>=20240930",
        "stable-ts-whisperless>=2.19.0",
        "fleep>=1.0.1"
    ],
    python_requires='>=3.10',
)