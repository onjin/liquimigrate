import os

from string import Template

from xml.dom import minidom
from xml.parsers.expat import ExpatError

from django.core.exceptions import ImproperlyConfigured
from django.db import DEFAULT_DB_ALIAS
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader


class NoMigrationsFound(Exception):
    pass


class InvalidChangelogFile(Exception):
    pass


def validate_app_names(loader, app_names):
    invalid_apps = []
    for app_name in app_names:
        if app_name not in loader.migrated_apps:
            invalid_apps.append(app_name)
    if invalid_apps:
        raise NoMigrationsFound(
                'No migrations present for: %s' % (
                    ', '.join(sorted(invalid_apps))))


def generate_changesets_text(
        connection, app_names=None, author=None, fake=False,
        skip_errors=False, indent=''):

    author = author or os.getlogin()

    loader = MigrationLoader(connection)
    graph = loader.graph

    if app_names:
        validate_app_names(loader, app_names)

        targets = [
                key for key in graph.leaf_nodes()
                if key[0] in app_names]
    else:
        targets = graph.leaf_nodes()
    plan = []
    seen = set()

    # Generate the plan
    for target in targets:
        for migration in graph.forwards_plan(target):
            if migration not in seen:
                node = graph.node_map[migration]
                plan.append(node)
                seen.add(migration)

    to_generate = []

    for node in plan:
        if node.key not in loader.applied_migrations:
            to_generate.append(node)

    executor = MigrationExecutor(connection)

    def cdata_lines(lines, indentation_level=2):
        indent_str = indentation_level * indent
        separator = u'\n%s' % indent_str
        if len(lines) > 1:
            return u'\n%s%s\n' % (indent_str, separator.join(lines))
        else:
            return lines[0]

    outputs = []

    changesett = Template(
        '$indent<changeSet author="$author" id="$id">$body$indent</changeSet>')
    cdatat = Template('<![CDATA[$body]]>')
    sqlt = Template('$indent$indent<sql>$body</sql>')
    rollbackt = Template(
        '$indent$indent<rollback>\n$indent$body\n$indent$indent</rollback>')

    forwardt = Template(
            'insert into django_migrations (app, name, applied) '
            'values (\'$app_label\', \'$migration_name\', now())')
    backwardt = Template(
            'delete from django_migrations where '
            'app=\'$app_label\' and name=\'$migration_name\'')

    for app_label, name in to_generate:
        migration = executor.loader.get_migration_by_prefix(
                                                    app_label, name)
        targets = [(app_label, migration.name)]
        forward_plan = [(executor.loader.graph.nodes[targets[0]], False)]
        backward_plan = [(executor.loader.graph.nodes[targets[0]], True)]

        try:
            sql_forward = executor.collect_sql(forward_plan)
        except Exception as ex:
            if skip_errors:
                sql_forward = ['-- skipped due to exception: %s' % ex]
            else:
                raise

        try:
            sql_backward = executor.collect_sql(backward_plan)
        except Exception as ex:
            if skip_errors:
                sql_backward = ['-- skipped due to exception: %s' % ex]
            else:
                raise

        changeset_id = u'django-%s-%s' % (app_label, migration.name)

        if fake:
            changeset_id += '-faked'

        ctx = {
                'indent': indent,
                'id': changeset_id,
                'author': author,
                'app_label': app_label,
                'migration_name': migration.name,
                }

        def rendertpl(tpl, **extra):
            tplctx = dict(ctx)
            tplctx.update(extra)
            return tpl.substitute(tplctx)

        changeset_parts = []

        if not fake:
            changeset_parts.append(u'\n'+rendertpl(sqlt, body=rendertpl(
                cdatat, body=cdata_lines(
                    sql_forward, indentation_level=2)+indent*2)))

        changeset_parts.append(rendertpl(sqlt, body=rendertpl(forwardt)))

        rollback_parts = []

        if not fake:
            rollback_parts.append(rendertpl(sqlt, body=rendertpl(
                cdatat, body=cdata_lines(
                    sql_backward, indentation_level=3)+indent*3)))

        rollback_parts.append(
                indent+rendertpl(sqlt, body=rendertpl(backwardt)))

        sep = u'\n'
        changeset_parts.append(rendertpl(
            rollbackt, body=sep.join(rollback_parts)))
        outputs.append(rendertpl(
            changesett, body=sep.join(changeset_parts)+u'\n'))
    return u'\n'.join(outputs)


def get_changelog_file_for_database(database=DEFAULT_DB_ALIAS):
    """get changelog filename for given `database` DB alias"""

    from django.conf import settings

    try:
        return settings.LIQUIMIGRATE_CHANGELOG_FILES[database]
    except AttributeError:
        if database == DEFAULT_DB_ALIAS:
            try:
                return settings.LIQUIMIGRATE_CHANGELOG_FILE
            except AttributeError:
                raise ImproperlyConfigured(
                        'Please set LIQUIMIGRATE_CHANGELOG_FILE or '
                        'LIQUIMIGRATE_CHANGELOG_FILES in your '
                        'project settings')
        else:
            raise ImproperlyConfigured(
                'LIQUIMIGRATE_CHANGELOG_FILES dictionary setting '
                'is required for multiple databases support')
    except KeyError:
        raise ImproperlyConfigured(
            "Liquibase changelog file is not set for database: %s" % database)


def find_target_migration_file(database=DEFAULT_DB_ALIAS, changelog_file=None):
    """Finds best matching target migration file"""

    if not database:
        database = DEFAULT_DB_ALIAS

    if not changelog_file:
        changelog_file = get_changelog_file_for_database(database)

    try:
        doc = minidom.parse(changelog_file)
    except ExpatError as ex:
        raise InvalidChangelogFile(
                'Could not parse XML file %s: %s' % (changelog_file, ex))

    try:
        dbchglog = doc.getElementsByTagName('databaseChangeLog')[0]
    except IndexError:
        raise InvalidChangelogFile(
            'Missing <databaseChangeLog> node in file %s' % (
                                                    changelog_file))
    else:
        nodes = list(filter(lambda x: x.nodeType is x.ELEMENT_NODE,
                            dbchglog.childNodes))
        if not nodes:
            return changelog_file

        last_node = nodes[-1]

        if last_node.tagName == 'include':
            last_file = last_node.attributes.get('file').firstChild.data
            return find_target_migration_file(
                    database=database, changelog_file=last_file)
        else:
            return changelog_file
