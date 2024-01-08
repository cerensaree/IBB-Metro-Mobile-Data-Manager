import setuptools

setuptools.setup(
    name="data-manager",
    version="0.3.2",
    author="Ceren Sare KILIÇARSLAN",
    author_email="cerensare@staj.com",
    description="Data Manager",
    url="https://gitlab.mantam.com.tr/ibb1/metro-mobile/data-manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms="all",
    classifiers=[
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Operating System :: Ubuntu",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],

    install_requires=['elasticsearch==6.8.2', 'elasticsearch-dsl==6.4.0', 'redis==5.0.1', 'psycopg2-binary'],
    packages=setuptools.find_packages(),
    scripts=['bin/data-manager']
)
