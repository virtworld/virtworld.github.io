# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 9
_modified_time = 1393463764.802842
_enable_loop = True
_template_filename = u'/usr/local/lib/python2.7/dist-packages/nikola/data/themes/bootstrap/templates/bootstrap_helper.tmpl'
_template_uri = u'bootstrap_helper.tmpl'
_source_encoding = 'ascii'
_exports = ['html_navigation_links', 'html_head', 'late_load_js']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 54
        __M_writer(u'\n\n')
        # SOURCE LINE 75
        __M_writer(u'\n\n\n')
        # SOURCE LINE 99
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_html_navigation_links(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        lang = context.get('lang', UNDEFINED)
        permalink = context.get('permalink', UNDEFINED)
        tuple = context.get('tuple', UNDEFINED)
        navigation_links = context.get('navigation_links', UNDEFINED)
        rel_link = context.get('rel_link', UNDEFINED)
        isinstance = context.get('isinstance', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 78
        __M_writer(u'\n')
        # SOURCE LINE 79
        for url, text in navigation_links[lang]:
            # SOURCE LINE 80
            if isinstance(url, tuple):
                # SOURCE LINE 81
                __M_writer(u'            <li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">')
                __M_writer(unicode(text))
                __M_writer(u'<b class="caret"></b></a>\n            <ul class="dropdown-menu">\n')
                # SOURCE LINE 83
                for suburl, text in url:
                    # SOURCE LINE 84
                    if rel_link(permalink, suburl) == "#":
                        # SOURCE LINE 85
                        __M_writer(u'                    <li class="active"><a href="')
                        __M_writer(unicode(permalink))
                        __M_writer(u'">')
                        __M_writer(unicode(text))
                        __M_writer(u'</a>\n')
                        # SOURCE LINE 86
                    else:
                        # SOURCE LINE 87
                        __M_writer(u'                    <li><a href="')
                        __M_writer(unicode(suburl))
                        __M_writer(u'">')
                        __M_writer(unicode(text))
                        __M_writer(u'</a>\n')
                # SOURCE LINE 90
                __M_writer(u'            </ul>\n')
                # SOURCE LINE 91
            else:
                # SOURCE LINE 92
                if rel_link(permalink, url) == "#":
                    # SOURCE LINE 93
                    __M_writer(u'                <li class="active"><a href="')
                    __M_writer(unicode(permalink))
                    __M_writer(u'">')
                    __M_writer(unicode(text))
                    __M_writer(u'</a>\n')
                    # SOURCE LINE 94
                else:
                    # SOURCE LINE 95
                    __M_writer(u'                <li><a href="')
                    __M_writer(unicode(url))
                    __M_writer(u'">')
                    __M_writer(unicode(text))
                    __M_writer(u'</a>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_html_head(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        permalink = context.get('permalink', UNDEFINED)
        favicons = context.get('favicons', UNDEFINED)
        description = context.get('description', UNDEFINED)
        title = context.get('title', UNDEFINED)
        use_cdn = context.get('use_cdn', UNDEFINED)
        translations = context.get('translations', UNDEFINED)
        blog_author = context.get('blog_author', UNDEFINED)
        mathjax_config = context.get('mathjax_config', UNDEFINED)
        rss_link = context.get('rss_link', UNDEFINED)
        striphtml = context.get('striphtml', UNDEFINED)
        abs_link = context.get('abs_link', UNDEFINED)
        has_custom_css = context.get('has_custom_css', UNDEFINED)
        len = context.get('len', UNDEFINED)
        _link = context.get('_link', UNDEFINED)
        use_bundles = context.get('use_bundles', UNDEFINED)
        blog_title = context.get('blog_title', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n    <meta charset="utf-8">\n')
        # SOURCE LINE 4
        if description:
            # SOURCE LINE 5
            __M_writer(u'    <meta name="description" content="')
            __M_writer(unicode(description))
            __M_writer(u'">\n')
        # SOURCE LINE 7
        __M_writer(u'    <meta name="author" content="')
        __M_writer(unicode(blog_author))
        __M_writer(u'">\n    <title>')
        # SOURCE LINE 8
        __M_writer(striphtml(unicode(title)))
        __M_writer(u' | ')
        __M_writer(striphtml(unicode(blog_title)))
        __M_writer(u'</title>\n    ')
        # SOURCE LINE 9
        __M_writer(unicode(mathjax_config))
        __M_writer(u'\n')
        # SOURCE LINE 10
        if use_bundles:
            # SOURCE LINE 11
            if use_cdn:
                # SOURCE LINE 12
                __M_writer(u'            <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.0/css/bootstrap-combined.min.css" rel="stylesheet">\n            <link href="/assets/css/all.css" rel="stylesheet" type="text/css">\n')
                # SOURCE LINE 14
            else:
                # SOURCE LINE 15
                __M_writer(u'            <link href="/assets/css/all-nocdn.css" rel="stylesheet" type="text/css">\n')
            # SOURCE LINE 17
        else:
            # SOURCE LINE 18
            if use_cdn:
                # SOURCE LINE 19
                __M_writer(u'            <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.0/css/bootstrap-combined.min.css" rel="stylesheet">\n')
                # SOURCE LINE 20
            else:
                # SOURCE LINE 21
                __M_writer(u'            <link href="/assets/css/bootstrap.min.css" rel="stylesheet" type="text/css">\n            <link href="/assets/css/bootstrap-responsive.min.css" rel="stylesheet" type="text/css">\n')
            # SOURCE LINE 24
            __M_writer(u'        <link href="/assets/css/rst.css" rel="stylesheet" type="text/css">\n        <link href="/assets/css/code.css" rel="stylesheet" type="text/css">\n        <link href="/assets/css/colorbox.css" rel="stylesheet" type="text/css"/>\n        <link href="/assets/css/theme.css" rel="stylesheet" type="text/css"/>\n')
            # SOURCE LINE 28
            if has_custom_css:
                # SOURCE LINE 29
                __M_writer(u'            <link href="/assets/css/custom.css" rel="stylesheet" type="text/css">\n')
        # SOURCE LINE 32
        if permalink:
            # SOURCE LINE 33
            __M_writer(u'      <link rel="canonical" href="')
            __M_writer(unicode(abs_link(permalink)))
            __M_writer(u'">\n')
        # SOURCE LINE 35
        __M_writer(u'    <!--[if lt IE 9]>\n      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js" type="text/javascript"></script>\n    <![endif]-->\n')
        # SOURCE LINE 38
        if rss_link:
            # SOURCE LINE 39
            __M_writer(u'        ')
            __M_writer(unicode(rss_link))
            __M_writer(u'\n')
            # SOURCE LINE 40
        else:
            # SOURCE LINE 41
            if len(translations) > 1:
                # SOURCE LINE 42
                for language in translations:
                    # SOURCE LINE 43
                    __M_writer(u'                <link rel="alternate" type="application/rss+xml" title="RSS (')
                    __M_writer(unicode(language))
                    __M_writer(u')" href="')
                    __M_writer(unicode(_link('rss', None, language)))
                    __M_writer(u'">\n')
                # SOURCE LINE 45
            else:
                # SOURCE LINE 46
                __M_writer(u'            <link rel="alternate" type="application/rss+xml" title="RSS" href="')
                __M_writer(unicode(_link('rss', None)))
                __M_writer(u'">\n')
        # SOURCE LINE 49
        if favicons:
            # SOURCE LINE 50
            for name, file, size in favicons:
                # SOURCE LINE 51
                __M_writer(u'            <link rel="')
                __M_writer(unicode(name))
                __M_writer(u'" href="')
                __M_writer(unicode(file))
                __M_writer(u'" sizes="')
                __M_writer(unicode(size))
                __M_writer(u'"/>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_late_load_js(context):
    __M_caller = context.caller_stack._push_frame()
    try:
        use_cdn = context.get('use_cdn', UNDEFINED)
        use_bundles = context.get('use_bundles', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 56
        __M_writer(u'\n')
        # SOURCE LINE 57
        if use_bundles:
            # SOURCE LINE 58
            if use_cdn:
                # SOURCE LINE 59
                __M_writer(u'            <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" type="text/javascript"></script>\n            <script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.0/js/bootstrap.min.js"></script>\n            <script src="/assets/js/all.js" type="text/javascript"></script>\n')
                # SOURCE LINE 62
            else:
                # SOURCE LINE 63
                __M_writer(u'            <script src="/assets/js/all-nocdn.js" type="text/javascript"></script>\n')
            # SOURCE LINE 65
        else:
            # SOURCE LINE 66
            if use_cdn:
                # SOURCE LINE 67
                __M_writer(u'            <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js" type="text/javascript"></script>\n            <script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.0/js/bootstrap.min.js"></script>\n')
                # SOURCE LINE 69
            else:
                # SOURCE LINE 70
                __M_writer(u'            <script src="/assets/js/jquery-1.10.2.min.js" type="text/javascript"></script>\n            <script src="/assets/js/bootstrap.min.js" type="text/javascript"></script>\n')
            # SOURCE LINE 73
            __M_writer(u'        <script src="/assets/js/jquery.colorbox-min.js" type="text/javascript"></script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


