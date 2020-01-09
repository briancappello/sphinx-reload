from setuptools import setup

import sphinx_reload


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="sphinx-reloader",
    author="Brian Cappello",
    author_email="briancappello@gmail.com",
    version=sphinx_reload.__version__,
    url="https://github.com/briancappello/sphinx-reload",
    license="MIT",
    description="Live preview your Sphinx documentation",
    long_description=long_description,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Documentation",
    ],
    keywords="sphinx live preview sync reload documentation",
    install_requires=[
        "livereload >= 2.5.1",
    ],
    py_modules=["sphinx_reload"],
    entry_points=dict(
        console_scripts=[
            "sphinx-reload = sphinx_reload:main",
        ],
    ),
)
