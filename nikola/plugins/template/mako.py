# -*- coding: utf-8 -*-

# Copyright © 2012-2014 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Mako template handlers"""
from __future__ import unicode_literals, print_function, absolute_import
import os
import shutil
import sys
import tempfile

from mako import util, lexer
from mako.lookup import TemplateLookup
from mako.template import Template
from markupsafe import Markup  # It's ok, Mako requires it

from nikola.plugin_categories import TemplateSystem
from nikola.utils import makedirs, get_logger, STDERR_HANDLER

LOGGER = get_logger('mako', STDERR_HANDLER)


class MakoTemplates(TemplateSystem):
    """Wrapper for Mako templates."""

    name = "mako"

    lookup = None
    cache = {}
    filters = {}

    def get_deps(self, filename):
        text = util.read_file(filename)
        lex = lexer.Lexer(text=text, filename=filename)
        lex.parse()

        deps = []
        for n in lex.template.nodes:
            keyword = getattr(n, 'keyword', None)
            if keyword in ["inherit", "namespace"]:
                deps.append(n.attributes['file'])
            # TODO: include tags are not handled
        return deps

    def set_directories(self, directories, cache_folder):
        """Create a template lookup."""
        cache_dir = os.path.join(cache_folder, '.mako.tmp')
        # Workaround for a Mako bug, Issue #825
        if sys.version_info[0] == 2:
            try:
                os.path.abspath(cache_dir).decode('ascii')
            except UnicodeEncodeError:
                cache_dir = tempfile.mkdtemp()
                LOGGER.warning('Because of a Mako bug, setting cache_dir to {0}'.format(cache_dir))

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
        self.lookup = TemplateLookup(
            directories=directories,
            module_directory=cache_dir,
            output_encoding='utf-8')

    def set_site(self, site):
        """Sets the site."""
        self.site = site
        self.filters.update(self.site.config['TEMPLATE_FILTERS'])

    def render_template(self, template_name, output_name, context):
        """Render the template into output_name using context."""
        context['striphtml'] = striphtml
        template = self.lookup.get_template(template_name)
        data = template.render_unicode(**context)
        if output_name is not None:
            makedirs(os.path.dirname(output_name))
            with open(output_name, 'w+') as output:
                output.write(data)
        return data

    def render_template_to_string(self, template, context):
        """ Render template to a string using context. """

        context = context.update(self.filters)

        return Template(template).render(**context)

    def template_deps(self, template_name):
        """Returns filenames which are dependencies for a template."""
        # We can cache here because dependencies should
        # not change between runs
        if self.cache.get(template_name, None) is None:
            template = self.lookup.get_template(template_name)
            dep_filenames = self.get_deps(template.filename)
            deps = [template.filename]
            for fname in dep_filenames:
                deps += self.template_deps(fname)
            self.cache[template_name] = tuple(deps)
        return list(self.cache[template_name])


def striphtml(text):
    return Markup(text).striptags()
