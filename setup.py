import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='nameseer',
      version='0.1.3',
      description='Thai person name classifier',
      long_description=long_description,
      long_description_content_type="text/markdown",      
      url='https://github.com/botx/nameseer',
      author='Pucktada Treeratpituk',
      author_email='pucktadt@bot.or.th',
      license='Apache Software License 2.0',
      packages=setuptools.find_packages('src'),
      package_dir={'': 'src'},
      package_data={'': ['*.pk']},
      python_requires=">=3.7.6",      
	include_package_data=True,
      install_requires=[
          'abydos',
          'scikit-learn',
          'nltk',
          'pythainlp',
      ],
      zip_safe=False)