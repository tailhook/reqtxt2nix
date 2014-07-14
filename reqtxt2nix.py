#!/usr/bin/env python

import sys
import os.path
import urllib.request
import json
import argparse
import subprocess

from pip.index import PackageFinder
from pip.req import parse_requirements, InstallRequirement


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("requirements", nargs="*",
        help="The requirement specifier, syntax is the same as for pip")
    ap.add_argument('-r', '--requirement',
        help="The requirements.txt file to parse (default requirements.txt)",
        dest="files", action="append", default=[])
    ap.add_argument('-f', '--find-links',
        help="Looks for the archives at the url or a directory",
        dest="find_links", action="append", default=[])
    ap.add_argument('--extra-index-url',
        help="Extra URLs for package indexes",
        dest="index_urls", action="append",
        default=['https://pypi.python.org/simple/'])
    ap.add_argument('-o', '--output', default=None,
        help="Write generated environment to file")
    options = ap.parse_args()

    if not options.requirements and not options.files:
        options.files = ['requirements.txt']

    all_req = []
    finder = PackageFinder(
        find_links=options.find_links,
        index_urls=options.index_urls,
        use_wheel=False,
        )
    for r in options.requirements:
        all_req.append(InstallRequirement.from_line(r))
    for f in options.files:
        print("F", f)
        all_req.extend(parse_requirements(f, finder=finder))

    if options.output:
        envname = os.path.splitext(os.path.basename(options.output))[0]
    else:
        envname = 'unnamed'

    with (open(options.output, 'wt') if options.output else sys.stdout) as out:
        out.write('{pkgs, '
                  'fetchurl ? pkgs.fetchurl, '
                  'python ? pkgs.python, pythonPackages ? pkgs.pythonPackages, '
                  'myEnvFun ? pkgs.myEnvFun}:\n')
        out.write('let\n')
        all_names = []
        for req in all_req:
            link = finder.find_requirement(req, True)
            prefix, _ext =  link.splitext()
            name = req.name.lower()
            version = finder._egg_info_matches(prefix, name, link)
            if link.hash_name:
                hash = link.hash
                hash_name = link.hash_name
            else:
                hash_name = 'sha256'
                stdout, _stderr = subprocess.Popen(['nix-prefetch-url',
                    '--type', hash_name,
                    link.url_without_fragment],
                    stdout=subprocess.PIPE,
                    ).communicate()
                hash = stdout.decode('ascii').strip()
            all_names.append(name)
            out.write('{} = pythonPackages.buildPythonPackage {{\n'
                .format(name))
            out.write('  name = "{}-{}";\n'.format(name, version))
            out.write('  src = fetchurl {\n')
            out.write('    url = "{}";\n'.format(link.url_without_fragment))
            out.write('    {} = "{}";\n'.format(hash_name, hash))
            out.write('  };\n')
            out.write('};\n')
        out.write('in myEnvFun {\n')
        out.write('  name = "{}";\n'.format(envname))
        out.write('  buildInputs = [\n')
        for name in all_names:
            out.write('    {}\n'.format(name))
        out.write('  ];\n')
        out.write('}')

    sys.stderr.write("""

Done. Now you can add the following to the ~/.nixpkgs/config.nix:

packageOverrides = pkgs: rec {{
    {name} = import ./{name}.nix {{
        inherit pkgs;
        python = pkgs.python{pyver};  # Or whatever version you prefer
        pythonPackages = pkgs.python{pyver}Packages;
    }};
}}

Then run:

nix-env -i env-{name}
load-env-{name}
""".format(name=envname, pyver='{0.major}{0.minor}'.format(sys.version_info)))


if __name__ == '__main__':
    main()
