#!/bin/python3
import sys
from easy_pack import EasyPackModule
from os import path, popen, system
from glob import glob
from sys import argv

module = EasyPackModule.read('.')

version = "release"

if '-version' in sys.argv:
	version = sys.argv[sys.argv.index('-version')+1]

module.package_data[""].clear()
module.files.clear()
folder = "build-" + version
s = popen("rm dependencies/*")
s.read()
for f in glob(folder + "/*"):
	module_file = f.replace(folder + "/", "")
	module.package_data[""].append(module_file)
	module.files.append("../" + folder + "/" + module_file)
	s = popen("./pbuild " + f + " dependencies")
	s.read()

for f in glob("dependencies/*"):
	dependency_file = f.replace("dependencies/", "")
	module.package_data[""].append(dependency_file)
	module.files.append("../dependencies/" + dependency_file)


if not path.exists('setup/setup.py') or path.getctime('__info__.py') > path.getctime('setup/setup.py'):
	print('package info file has changed, rebuilding setup')
module.create_setup_files('../setup')
build = module.build_module('python-build', "bdist_wheel")
if build:
	print('build succeeded')
	if '-upload' in sys.argv:
		username = ''
		if '-user' in sys.argv:
			username = sys.argv[sys.argv.index('-user')+1]
		password = ''
		if '-password' in sys.argv:
			password = sys.argv[sys.argv.index('-password')+1]
		repository = ''
		if '-repository' in sys.argv:
			repository = sys.argv[sys.argv.index('-repository')+1]
		system('cd ' + build + '; twine upload dist/*' + ((' --repository-url  ' + repository) if repository else '') + ((' -u ' + username) if username else '') + ((' -p ' + password) if password else ''))
	else:
		print('use twine upload --repository-url [pypi-repository-url] dist/* to upload the package')
	if '-install' in sys.argv:
		system('cd ' + build + '; python3.7 -m pip install .')
	module.save('.')
else:
	print('build failed')
