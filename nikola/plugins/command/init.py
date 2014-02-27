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

from __future__ import print_function
import os
import shutil
import codecs
import json

from mako.template import Template

import nikola
from nikola.nikola import DEFAULT_TRANSLATIONS_PATTERN
from nikola.plugin_categories import Command
from nikola.utils import get_logger, makedirs, STDERR_HANDLER
from nikola.winutils import fix_git_symlinked

LOGGER = get_logger('init', STDERR_HANDLER)

SAMPLE_CONF = {
    'BLOG_AUTHOR': "Your Name",
    'BLOG_TITLE': "Demo Site",
    'SITE_URL': "http://getnikola.com/",
    'BLOG_EMAIL': "joe@demo.site",
    'BLOG_DESCRIPTION': "This is a demo site for Nikola.",
    'DEFAULT_LANG': "en",
    'THEME': 'bootstrap3',
    'COMMENT_SYSTEM': 'disqus',
    'COMMENT_SYSTEM_ID': 'nikolademo',
    'TRANSLATIONS_PATTERN': DEFAULT_TRANSLATIONS_PATTERN,
    'POSTS': """(
("posts/*.rst", "posts", "post.tmpl"),
("posts/*.txt", "posts", "post.tmpl"),
)""",
    'PAGES': """(
("stories/*.rst", "stories", "story.tmpl"),
("stories/*.txt", "stories", "story.tmpl"),
)""",
    'COMPILERS': """{
"rest": ('.rst', '.txt'),
"markdown": ('.md', '.mdown', '.markdown'),
"textile": ('.textile',),
"txt2tags": ('.t2t',),
"bbcode": ('.bb',),
"wiki": ('.wiki',),
"ipynb": ('.ipynb',),
"html": ('.html', '.htm'),
# PHP files are rendered the usual way (i.e. with the full templates).
# The resulting files have .php extensions, making it possible to run
# them without reconfiguring your server to recognize them.
"php": ('.php',),
# Pandoc detects the input from the source filename
# but is disabled by default as it would conflict
# with many of the others.
# "pandoc": ('.rst', '.md', '.txt'),
}""",
    'REDIRECTIONS': [],
}


# In order to ensure proper escaping, all variables but the three
# pre-formatted ones are handled by json.dumps().
def prepare_config(config):
    """Parse sample config with JSON."""
    p = config.copy()
    p.update(dict((k, json.dumps(v)) for k, v in p.items()
             if k not in ('POSTS', 'PAGES', 'COMPILERS')))
    return p


class CommandInit(Command):

    """Create a new site."""

    name = "init"

    doc_usage = "[--demo] folder"
    needs_config = False
    doc_purpose = "create a Nikola site in the specified folder"
    cmd_options = [
        {
            'name': 'demo',
            'long': 'demo',
            'default': False,
            'type': bool,
            'help': "Create a site filled with example data.",
        }
    ]

    @classmethod
    def copy_sample_site(cls, target):
        lib_path = cls.get_path_to_nikola_modules()
        src = os.path.join(lib_path, 'data', 'samplesite')
        shutil.copytree(src, target)
        fix_git_symlinked(src, target)

    @classmethod
    def create_configuration(cls, target):
        lib_path = cls.get_path_to_nikola_modules()
        template_path = os.path.join(lib_path, 'conf.py.in')
        conf_template = Template(filename=template_path)
        conf_path = os.path.join(target, 'conf.py')
        with codecs.open(conf_path, 'w+', 'utf8') as fd:
            fd.write(conf_template.render(**prepare_config(SAMPLE_CONF)))

    @classmethod
    def create_empty_site(cls, target):
        for folder in ('files', 'galleries', 'listings', 'posts', 'stories'):
            makedirs(os.path.join(target, folder))

    @staticmethod
    def get_path_to_nikola_modules():
        return os.path.dirname(nikola.__file__)

    def _execute(self, options={}, args=None):
        """Create a new site."""
        if not args:
            print("Usage: nikola init folder [options]")
            return False
        target = args[0]
        if not options or not options.get('demo'):
            self.create_empty_site(target)
            LOGGER.info('Created empty site at {0}.'.format(target))
        else:
            self.copy_sample_site(target)
            LOGGER.info("A new site with example data has been created at "
                        "{0}.".format(target))
            LOGGER.info("See README.txt in that folder for more information.")

        self.create_configuration(target)
