
import os
import fnmatch
import locale
import subprocess

DOIT_CONFIG = {
    'default_tasks': ['flake8', 'test'],
    'reporter': 'executed-only',
}


def recursive_glob(path, pattern):
    """recursively walk path directories and return files matching the pattern"""
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


def task_flake8():
    """flake8 - static check for python files"""
    yield {
        'name': os.getcwd(),
        'actions': ['flake8 --ignore=E501 .'],
    }


def task_locale():
    """set environ locale vars used in nikola tests"""
    def set_nikola_test_locales():
        try:
            out = subprocess.check_output(['locale', '-a'])
            locales = []
            languages = set()
            for line in out.splitlines():
                if line.endswith('.utf8') and '_' in line:
                    lang = line.split('_')[0]
                    if lang not in languages:
                        try:
                            locale.setlocale(locale.LC_ALL, line)
                        except:
                            continue
                        languages.add(lang)
                        locales.append((lang, line))
                        if len(locales) == 2:
                            break
            if len(locales) != 2:
                return False  # task failed
            else:
                os.environ['NIKOLA_LOCALE_DEFAULT'] = ','.join(locales[0])
                os.environ['NIKOLA_LOCALE_OTHER'] = ','.join(locales[1])
        finally:
            # restore to default locale
            locale.resetlocale()

    return {'actions': [set_nikola_test_locales], 'verbosity': 2}


def task_test():
    """run unit-tests using nose"""
    return {
        'task_dep': ['locale'],
        'actions': ['nosetests --with-doctest --doctest-options=+NORMALIZE_WHITESPACE --logging-filter=-yapsy'],
    }


def task_coverage():
    """run unit-tests using nose"""
    return {
        'task_dep': ['locale'],
        'actions': ['nosetests --with-coverage --cover-package=nikola --with-doctest --doctest-options=+NORMALIZE_WHITESPACE --logging-filter=-yapsy'],
        'verbosity': 2,
    }


def task_gen_completion():
    """generate tab-completion scripts"""
    cmd = 'nikola tabcompletion --shell {0} --hardcode-tasks > _nikola_{0}'
    for shell in ('bash', 'zsh'):
        yield {
            'name': shell,
            'actions': [cmd.format(shell)],
            'targets': ['_nikola_{0}'.format(shell)],
        }
