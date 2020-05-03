from setuptools import setup, find_packages


setup(
    name="idenaTelegramUpdater",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["Twisted>=17.9.0", "attrs", "python-telegram-bot", "treq"],
    extras_require={"dev": ["black", "pylint"]},
)
