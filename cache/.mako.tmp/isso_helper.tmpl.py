# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1393463764.689011
_enable_loop = True
_template_filename = u'/usr/local/lib/python2.7/dist-packages/nikola/data/themes/base/templates/isso_helper.tmpl'
_template_uri = u'isso_helper.tmpl'
_source_encoding = 'utf-8'
_exports = ['comment_form', 'comment_link', 'comment_link_script']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 7
        __M_writer(u'\n\n')
        # SOURCE LINE 13
        __M_writer(u'\n\n\n')
        # SOURCE LINE 20
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_comment_form(context,url,title,identifier):
    __M_caller = context.caller_stack._push_frame()
    try:
        comment_system_id = context.get('comment_system_id', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3
        if comment_system_id:
            # SOURCE LINE 4
            __M_writer(u'        <div data-title="')
            __M_writer(filters.url_escape(unicode(title)))
            __M_writer(u'" id="isso-thread"></div>\n        <script src="')
            # SOURCE LINE 5
            __M_writer(unicode(comment_system_id))
            __M_writer(u'js/embed.min.js" data-isso="')
            __M_writer(unicode(comment_system_id))
            __M_writer(u'"></script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_comment_link(context,link,identifier):
    __M_caller = context.caller_stack._push_frame()
    try:
        comment_system_id = context.get('comment_system_id', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 9
        __M_writer(u'\n')
        # SOURCE LINE 10
        if comment_system_id:
            # SOURCE LINE 11
            __M_writer(u'        <a href="')
            __M_writer(unicode(link))
            __M_writer(u'#isso-thread">Comments</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_comment_link_script(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        comment_system_id = context.get('comment_system_id', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 16
        __M_writer(u'\n')
        # SOURCE LINE 17
        if comment_system_id:
            # SOURCE LINE 18
            __M_writer(u'        <script src="')
            __M_writer(unicode(comment_system_id))
            __M_writer(u'js/count.min.js" data-isso="')
            __M_writer(unicode(comment_system_id))
            __M_writer(u'"></script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


