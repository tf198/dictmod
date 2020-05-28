import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dictmod",
    version="0.0.1",
    author="Tris Forster",
    author_email="tris@shoddynet.org",
    description="Work with nested dictionaries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tf198/dictmod",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)

