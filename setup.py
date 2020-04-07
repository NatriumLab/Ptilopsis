from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kuriyama-ptilopsis",
    version='0.1.0',
    description='A library to support command system(native and improve) for python-mirai(kuriyama)',
    author='Chenwe-i-lin',
    author_email="Chenwe_i_lin@outlook.com",
    url="https://github.com/Chenwe-i-lin/python-mirai",
    packages=find_packages(include=("ptilopsis", "ptilopsis.*")),
    python_requires='>=3.7',
    keywords=["oicq qq qqbot command", ],
    install_requires=[
        "kuriyama"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: AGPLv3 License',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent"
    ]
)