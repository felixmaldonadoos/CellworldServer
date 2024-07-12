from setuptools import setup

import os
if os.path.isfile('./json_cpp/README.md'):
	with open('./json_cpp/README.md') as f:
		long_description = f.read()
else:
	long_description = ''
setup(name='json-cpp',description='a better json library',author='german espinosa',author_email='germanespinosa@gmail.com',long_description=long_description,long_description_content_type='text/markdown',packages=['json_cpp'],install_requires=['requests'],license='MIT',version='1.0.134',zip_safe=False)
