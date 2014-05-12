from setuptools import setup

setup(name="pyshipwire",
      version="0.0.0",
      description="Python wrapper for the shipwire API.",
      url="https://github.com/alephobjects/pyshipwire",
      author="Aeva Palecek",
      author_email="aeva@alephobjects.com",
      license="GPLv3",
      packages=["shipwire"],
      package_data={'': ['countries.csv']},
      zip_safe=False,

      install_requires = [
          "requests",
          "lxml", 
          "BeautifulSoup",
        ])
