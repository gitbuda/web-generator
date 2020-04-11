"""Simple static web generator.

Usage:
    generate.py [--descriptor-file=<path>]
    generate.py -h | --help

Arguments:
    -h --help                  Shows this screen.
    --descriptor-file=<path>   Path to a file describing how to generate
                               the web [default: descriptor.yaml].
"""

from dataclasses import dataclass
from os import mkdir, makedirs
from os.path import join, exists, split
from sys import exit
from typing import List

from jinja2 import Environment, FileSystemLoader, Template
from markdown import markdown
from shutil import copy
from yaml import safe_load


def load_yaml(path):
    """Loads YAML from a file on the given path into a dict object.

    Args:
        path: Path to the YAML file.

    Returns:
        A dict object with the content of the YAML file.
    """
    try:
        with open(path, 'r') as stream:
            return safe_load(stream)
    except Exception as e:
        print(e)
        exit(1)


@dataclass
class IndexContext:
    output_directory: str
    template: Template
    posts: List


def generate_index(context: IndexContext):
    """Generates index.html file within context.output_directory.

    Args:
        context: All data required to generate the index file.
    """
    context.template.stream(
        posts=context.posts).dump(join(context.output_directory, 'index.html'))


@dataclass
class CopyContext:
    dst_directory: str
    files: List


def make_copy(context: CopyContext):
    """Copy context.files to the given dst_directory.

    Args:
        context: All date required to make the copy operation. context.files
            is a list of pairs where the first element is src file and the
            second element is relative destination file path. Final
            destination directory will be defined by joining
            context.dst_directory and the second path within each list item.
            If necessary, all required directories will be created.
    """
    for src, dst in context.files:
        dst_file = join(context.dst_directory, dst)
        directory, _ = split(dst_file)
        makedirs(directory, exist_ok=True)
        copy(src, dst_file)


@dataclass
class BlogContext:
    base_url: str
    output_directory: str
    post_template: Template
    posts_content_root: str
    posts_descriptor: List


def generate_blog(context: BlogContext):
    """Generate blog posts under {context.output_directory}/posts/.

    Args:
        context: All data required to generate the blog post files.
    """
    for post in context.posts_descriptor:
        if 'url' in post:
            # This is a standalone post somewhere else / just skip it.
            continue
        post_content_directory = join(
            context.posts_content_root, post['directory'])
        post_content_file = join(post_content_directory, 'README.md')
        post_id = post['id']
        post_directory = join(
            context.output_directory, 'posts', post_id)
        makedirs(post_directory, exist_ok=True)
        post_html_path = join(post_directory, 'index.html')
        post_content_md = open(post_content_file).read()
        post_content_html = markdown(
            post_content_md,
            extensions=['codehilite', 'fenced_code'],
            extension_configs={
                'codehilite': {
                    'guess_lang': True,
                    'linenums': False,
                    'css_class': 'highlight'}})
        post_url = context.base_url + "/posts/" + post_id + "/index.html"
        context.post_template.stream(
            post=post_content_html,
            post_id=post_id,
            post_url=post_url).dump(post_html_path)
        # Artefacts are referenced from the generated files.
        # The only supported operation is copy for now.
        if 'artefacts' in post:
            for artefact in post['artefacts']:
                src = join(post_content_directory, artefact)
                dst = join(post_directory, artefact)
                directory, _ = split(dst)
                makedirs(directory, exist_ok=True)
                copy(src, dst)


def generate_web(descriptor):
    """Generate the whole web based on the descriptor.

    Args:
        descriptor: A dict like object with all data to generate the web. For
            the example take a look at the top level README.md file. Supported
            operations are: index (generate_index), copy (make_copy),
            blog (generate_blog).
    """
    if not exists(descriptor['site_directory']):
        mkdir(descriptor['site_directory'])

    template_loader = FileSystemLoader(
        searchpath=descriptor['templates_directory'])
    template_environment = Environment(loader=template_loader)

    # Generate index.
    index_template = template_environment.get_template(
        descriptor['index']['index_template'])
    index_context = IndexContext(
        descriptor['site_directory'],
        index_template,
        descriptor['blog']['posts'])
    generate_index(index_context)

    # Copy assets.
    copy_context = CopyContext(
        descriptor['site_directory'],
        descriptor['copy']['files'])
    make_copy(copy_context)

    # Generate blog posts.
    blog_post_template = template_environment.get_template(
        descriptor['blog']['post_template'])
    blog_context = BlogContext(
        descriptor['base_url'],
        descriptor['site_directory'],
        blog_post_template,
        descriptor['blog']['posts_content_directory'],
        descriptor['blog']['posts'])
    generate_blog(blog_context)


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)
    descriptor = load_yaml(args['--descriptor-file'])
    generate_web(descriptor)
