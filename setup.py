from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='pyxml3',
    version='0.0.2',
    license='MIT',
    author='Andrew Scott',
    author_email='imgurbot12@gmail.com',
    url='https://github.com/imgurbot12/pyxml',
    description="Pure python3 Alternative to stdlib xml.etree with HTML support",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    packages=find_packages(),
    install_requires=[
        'dataclasses',
        'typing_extensions',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
