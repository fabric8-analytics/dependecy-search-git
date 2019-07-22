"""Node parser."""

from parsers.parser_base import Parser
from six import iteritems
from werkzeug.exceptions import BadRequest
import json


class NodeParser(Parser):
    """Parser for parsing npm list --prod --json."""

    @staticmethod
    def parse_output_files(files):
        """Parse output file."""
        if len(files) > 1:
            raise BadRequest("Please provide a single file with name npmlist.json")
        content = json.loads(files[0].read().decode('utf-8'))
        dependencies = content.get('dependencies')
        direct_dependencies = set()
        transitive_dependencies = set()
        if dependencies:
            for k, v in iteritems(dependencies):
                dependency_name = k
                dependency_version = v['version']
                direct_dependencies.add("npm:{name}:{version}".format(
                    name=dependency_name, version=dependency_version))
                if v.get('dependencies'):
                    NodeParser.get_transitive_dependencies(v['dependencies'],
                                                           transitive_dependencies)

        return direct_dependencies, transitive_dependencies

    @staticmethod
    def get_transitive_dependencies(content, transitive_dependencies):
        """Get transitive dependencies."""
        for k, v in iteritems(content):
            if v.get('dependencies'):
                NodeParser.get_transitive_dependencies(v['dependencies'],
                                                       transitive_dependencies)
            else:
                dependency_name = k
                dependency_version = v['version']
                transitive_dependencies.add("npm:{name}:{version}".format(
                    name=dependency_name, version=dependency_version))
