from pybuilder.core import use_plugin, init, Author

use_plugin('python.core')
use_plugin('python.install_dependencies')
use_plugin('python.distutils')
use_plugin('python.unittest')
use_plugin('python.flake8')
use_plugin('python.coverage')
use_plugin('python.integrationtest')
use_plugin('python.pylint')

name = 'aries'
default_task = 'publish'
authors = [Author('Riccardo Bonetto', 'riccardo.bonetto@tu-dresden.de'), Author('Ilya Sychev', 'ilya.sychev@tu-dresden.de')]
license = 'MIT License'
summary = 'ARIES - Low Voltage smArt gRid dIscrete EventSimulator to Enable Large Scale Learning in thePower Distribution Networks'
url = 'https://github.com/comnetstud/ARIES'
version = '0.1'


@init
def set_properties(project):
    project.set_property('coverage_break_build', False)  # default is True
    project.set_property('distutils_issue8876_workaround_enabled', True)
    project.set_property('unittest_module_glob', 'test_*.py')
    project.set_property('integrationtest_file_glob', 'itest_*.py')
    project.set_property('integrationtest_inherit_environment', True)
    project.set_property('pylint_options', ['--rcfile=pylint/pylint.cfg'])

    project.set_property('unittest_runner', (
        lambda stream: __import__('xmlrunner').XMLTestRunner(
            output=project.expand_path('$dir_target/reports/unittests'),
            stream=stream), '_make_result'))
