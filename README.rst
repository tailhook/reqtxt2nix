==========
reqtxt2nix
==========

reqtxt2nix is a small utility which converts ``requirements.txt`` file into
``.nix`` file that contains myEnvFun_  declaration. I.e. it helps to build
pythonic dev environments in nix.

Main features:

* Generates nice short and clean dev environment expression
* Makes specific versions of python libraries from requirements.txt
* Writes url/hash code boiler plate
* Doesn't execute untrusted code (I mean setup.py)
* Very short and simple script

Running::

    reqtxt2nix -r requirements.txt -o ~/.nixpkgs/myproject.nix

This generates the ``~/.nixpkgs/myproject.nix`` and prints instructions on
how to activate it. Which boils down to::

Add the following to the ``~/.nixpkgs/config.nix``::

    packageOverrides = pkgs: rec {
        myproject = import ./myproject.nix {
            inherit pkgs;
            python = pkgs.python34;  # Or whatever version you prefer
            pythonPackages = pkgs.python34Packages;
        };
    }

The default python printed is one, which runs ``reqtxt2nix``, usually you
want to change that. Remember to change the ``python34Packages`` too.

Then install environment with::

    nix-env -i env-myproject

Now, to activate the environment run::

    load-env-myproject

It works very similarly to how virtualenv works.


Additional Options
==================

``reqtxt2nix`` supports the folowing options which have same meaning as
in pip:

* --index-url
* --find-links
* --requirement

All supported both on a command-line and in ``requirements.txt`` itself.

Specifying packages on a command-line also work (however discouraged)::

    ./reqtxt2nix markupsafe==0.23 "jinja2>=2.5" -o ~/.nixpkgs/jinja.nix

Always using ``-o`` or ``--output`` is recommended, as well as writing file
into ``~/.nixpkgs/something.nix``.


Dependency Tracking
===================

The ``reqtxt2nix`` does *absolutely nothing* to track dependencies. The reasons
are following:

* You are probably use ``pip freeze`` to generate ``requirements.txt`` so all
  dependencies are already in the list
* You don't want to get python packages from nixpkgs anyway because you have
  frozen specific versions of each dependency

We don't add C dependencies too, because they are not declared in python.

The main idea is that it's easy to add ``buildInputs`` yourself
(the ``reqtxt2nix`` only removes burden of adding urls and hashsums from you).

When its stated that utility doesn't track dependencies, it doesn't mean
utility cancels nix's own tracking. I.e. you will fail to build packages if
there are requirements, so you'll see error and will be able to fix pretty
quickly.


Customization
=============

There are three types of customizations.

*First* one is change python version. It's outlined above.

*Second* one is customizing the environment. The simplest way to do it is
overload a function::

    let myEnvFun = args: pkgs.myEnvFun args // {
        shell = '${pkgs.zsh}/bin/zsh';
    }

    in {
        packageOverrides = pkgs: rec {
            myproject = import ./myproject.nix {
                inherit pkgs;
                inherit myEnvFun;        # pass our custimized version
                python = pkgs.python34;
                pythonPackages = pkgs.python34Packages;
            };
        }
    }

You can also customize other aspects of ``myEnvFun``.

The *third* one is altering packages. You usually want to change two things:

* ``buildInputs = [ some package names ];`` -- to set dependencies
* ``doCheck = false;`` -- in case tests need more dependencies that you want

Note that ``buildInputs`` should contain raw variable references (no ``.``
dot) when referring to packages in same environment (actually sibling ``let``
bindings). For system packages ``pkgs.package_name`` notation should be used.
And for system *python* packages ``pythonPackages.package_name`` (regardless of
real python version, it's overriden on import).

Other useful modifications:

* Some python packages are not "pure", i.e. them download files when building.
  This must be fixed by hand
* Adding (specific versions of) C librarie
* Use package from nixpkgs but override only version (and url/hash)

See nixos documentation on how to do all these things.


Updating Environment
====================

Since dependencies are sorted in same order as in original ``requirements.txt``
you can generate new config into ``~/.nixpkgs/myproject.nix.new`` and use your
favorite merge tool. Just be sure you don't overwrite previous file as it's
likely to contain some customizations.


Related Projects
================

* python2nix_ -- tries to be more smart on metadata, but creates expressions
  one by one (while we concentrate on making build environments)
* pypi2nix_ -- has it's own specification format and also tries to be smarter
  (so more complex to use) than needed for me.

.. _myEnvFun: https://nixos.org/wiki/Howto_develop_software_on_nixos
.. _pypi2nix: https://github.com/garbas/pypi2nix
.. _python2nix: https://github.com/proger/python2nix



