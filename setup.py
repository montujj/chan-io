from setuptools import setup, find_packages

setup(
    name="chan-io",
    version="1.0.0",
    author="Montu Jariwala",
    author_email="montujj@gmail.com",
    description="Chan I/O Tool - Export/Import .chan camera animation files for Maya and Nuke",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/montujj/chan-io",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "PySide2>=5.15.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
