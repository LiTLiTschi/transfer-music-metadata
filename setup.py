from setuptools import setup, find_packages

setup(
    name="transfer-music-metadata",
    version="1.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mutagen>=1.47.0",
        "pyyaml>=6.0",
        "colorama>=0.4.6",
        "tqdm>=4.66.0",
    ],
    entry_points={
        "console_scripts": [
            "tmm=tmm.__main__:main",
        ],
    },
    python_requires=">=3.8",
    author="Transfer Music Metadata",
    description="Transfer metadata tags between audio files (MP3, M4A, FLAC, WAV)",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/LiTLiTschi/transfer-music-metadata",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
