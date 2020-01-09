"""
Live reload your Sphinx documentation.
"""
import argparse
import glob
import os

import livereload
import livereload.watcher

__version__ = "0.2.0"


def get_recursive_watcher():
    def is_glob_changed(self, path, ignore=None):
        for file in glob.glob(path, recursive=True):
            if self.is_file_changed(file, ignore):
                return True
        return False

    return type('RecursiveGlobWatcher',
                (livereload.watcher.get_watcher_class(),),
                {'is_glob_changed': is_glob_changed})()


class _SphinxResourceFactory:
    @staticmethod
    def get_documentation_root(makefile_path):
        if os.path.isfile(makefile_path):
            makefile_path = os.path.dirname(makefile_path)
        return os.path.abspath(makefile_path)

    @staticmethod
    def estimate_source_directory(doc_root):
        if os.path.isfile(os.path.join(doc_root, "source", "conf.py")):
            return os.path.join(doc_root, "source")
        elif os.path.isfile(os.path.join(doc_root, "conf.py")):
            return doc_root
        raise ValueError(
            f"Failed to estimate documentation source dir from path '{doc_root}'")

    @staticmethod
    def get_build_directory(doc_root):
        return os.path.join(doc_root, "_build")

    @staticmethod
    def get_make_command(build_directory):
        make_cmd = "make html"
        if build_directory is not None:
            make_cmd += f" BUILDDIR={build_directory}"
        return make_cmd

    @staticmethod
    def get_html_directory(build_directory):
        return os.path.join(build_directory, "html")


class SphinxServer:
    def __init__(self):
        self._watch_patterns = []
        self._sphinx = _SphinxResourceFactory()

    def watch(self, *glob_names):
        self._watch_patterns.extend(glob_names)

    def _run(self, build_func, source_dir, html_dir, port, host):
        server = livereload.Server(watcher=get_recursive_watcher())
        watch_patterns = self._watch_patterns + [
            f'{source_dir}/conf.py',
            f'{source_dir}/_static/*.css',
            f'{source_dir}/_templates/*.html',
            f'{source_dir}/*.rst',
            f'{source_dir}/**/*.rst',
        ]
        for pattern in watch_patterns:
            server.watch(pattern, build_func)

        build_func()  # Do an initial build.
        server.serve(root=html_dir, host=host, port=port, restart_delay=0.2)

    def run(self, doc_root, build_dir=None, host="localhost", port=5500):
        source_dir = self._sphinx.estimate_source_directory(doc_root)
        doc_root = self._sphinx.get_documentation_root(doc_root)
        if build_dir is None:
            build_dir = self._sphinx.get_build_directory(doc_root)
        html_dir = self._sphinx.get_html_directory(build_dir)
        build_cmd = self._sphinx.get_make_command(build_dir)

        def build_func():
            print('starting build... ', flush=True)
            livereload.shell(build_cmd, cwd=doc_root)()
            print('build complete!', flush=True)

        self._run(build_func, source_dir, html_dir, port=port, host=host)


def _parse_cli_args():
    parser = argparse.ArgumentParser(prog="sphinx-reload")
    parser.add_argument(
        '--version',
        action='version',
        version=f'v{__version__}',
    )
    parser.add_argument(
        "documentation_root",
        help="Your documentation's root directory "
             "(i.e. where `sphinx-build` put the Makefile).",
    )
    parser.add_argument(
        "--build-dir",
        help="The desired build directory.",
        default=None,
    )
    parser.add_argument(
        "--host",
        help="The host to serve files.",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=5500,
        type=int,
        help="The port number from which to serve your documentation.",
    )
    parser.add_argument(
        "--watch",
        metavar="PATTERN",
        default=[],
        nargs="+",
        help="File patterns to watch for changes that should rebuild the docs."
    )
    return parser.parse_args()


def main():
    server = SphinxServer()
    args = _parse_cli_args()
    if args.watch:
        server.watch(*args.watch)
    server.run(args.documentation_root,
               build_dir=args.build_dir,
               host=args.host,
               port=args.port)


if __name__ == "__main__":
    main()
