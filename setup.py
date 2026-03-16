"""Setup script for PronounceIt."""

from setuptools import setup, find_packages

setup(
    name="pronounceit",
    version="0.1.0",
    description="Uttalsträning för alla språk med visuell feedback och spektrogram",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="PronounceIt Team",
    license="MIT",
    url="https://github.com/yeager/PronounceIt",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "pronounceit": ["../data/**/*", "../po/*.po", "../po/*.pot"],
    },
    data_files=[
        (
            "share/applications",
            ["desktop/se.pronounceit.PronounceIt.desktop"],
        ),
        (
            "share/metainfo",
            ["desktop/se.pronounceit.PronounceIt.metainfo.xml"],
        ),
    ],
    entry_points={
        "gui_scripts": ["pronounceit = pronounceit.__main__:main"],
    },
    install_requires=[
        "PyGObject>=3.42.0",
        "pyaudio>=0.2.13",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "matplotlib>=3.7.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
)
