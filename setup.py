from setuptools import setup, find_packages

setup(
    name="sdrpy",  # Replace with your package name
    version="0.1.0",  # Replace with your version number
    description="Simple analytics for dtcc data",
    author="Anchorblock",
    author_email="qavi@anchorblock.vc",
    packages=find_packages(),  # Automatically finds packages
    install_requires=[  # List external dependencies here
        "numpy",
        "pandas",
        "matplotlib",
        "tabulate",
        "python-dotenv"

    ],
)

