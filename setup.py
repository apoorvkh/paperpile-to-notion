from setuptools import find_packages, setup

requirements = ["requests", "bibtexparser", "PyDrive2"]

setup(
    name="paperpile_to_notion",
    version="1.0.0",
    url="https://github.com/apoorvkh/paperpile-to-notion",
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.9",
    ],
    description="Python tool for syncing your Paperpile library with Notion database.",
    packages=find_packages(),
    entry_points = {
        "console_scripts": [
            "paperpile_to_notion = paperpile_to_notion.__main__:main",
        ]
    }
)
