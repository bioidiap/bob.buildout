#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Deployment utilities for sphinx documentation via webDAV.

Requires you ``pip install webdavclient3``
"""


import os
import sys
import logging

logger = logging.getLogger("deploy")

_SERVER = "http://www.idiap.ch"

_WEBDAV_PATHS = {
    True: {  # stable?
        False: {  # visible?
            "root": "/private-upload",
            "conda": "/conda",
            "docs": "/docs",
        },
        True: {  # visible?
            "root": "/public-upload",
            "conda": "/conda",
            "docs": "/docs",
        },
    },
    False: {  # stable?
        False: {  # visible?
            "root": "/private-upload",
            "conda": "/conda/label/beta",
            "docs": "/docs",
        },
        True: {  # visible?
            "root": "/public-upload",
            "conda": "/conda/label/beta",
            "docs": "/docs",
        },
    },
}
"""Default locations of our webdav upload paths"""


def _setup_webdav_client(server, root, username, password):
    """Configures and checks the webdav client."""

    # setup webdav connection
    webdav_options = dict(
        webdav_hostname=server,
        webdav_root=root,
        webdav_login=username,
        webdav_password=password,
    )

    from webdav3.client import Client

    retval = Client(webdav_options)
    assert retval.valid()

    return retval


def deploy_documentation(
    path,
    package,
    stable,
    latest,
    public,
    branch,
    tag,
    username,
    password,
    dry_run,
):
    """Deploys sphinx documentation to the appropriate webdav locations.

    Parameters
    ==========

    path : str
        Path leading to the root of the documentation to be deployed

    package : str
        Full name (with namespace) of the package being treated

    stable : bool
        Indicates if the documentation corresponds to the latest stable build

    latest : bool
        Indicates if the documentation being deployed correspond to the latest
        stable for the package or not.  In case the documentation comes from a
        patch release which is not on the master branch, please set this flag
        to ``False``, which will make us avoid deployment of the documentation
        to ``master`` and ``stable`` sub-directories.

    public : bool
        Indicates if the documentation is supposed to be distributed publicly
        or privatly (within Idiap network)

    branch : str
        The name of the branch for the current build

    tag : str
        The name of the tag currently built (may be ``None``)

    username : str
        The name of the user on the webDAV server to use for uploading the
        package

    password : str
        The password of the user on the webDAV server to use for uploading the
        package

    dry_run : bool
        If we're supposed to really do the actions, or just log messages.

    """

    # uploads documentation artifacts
    if not os.path.exists(path):
        raise RuntimeError(
            "Documentation is not available at %s - "
            "ensure documentation is being produced for your project!" % path
        )

    server_info = _WEBDAV_PATHS[stable][public]
    davclient = _setup_webdav_client(
        _SERVER, server_info["root"], username, password
    )

    remote_path_prefix = "%s/%s" % (server_info["docs"], package)

    # finds out the correct mixture of sub-directories we should deploy to.
    # 1. if ref-name is a tag, don't forget to publish to 'master' as well -
    # all tags are checked to come from that branch
    # 2. if ref-name is a branch name, deploy to it
    # 3. in case a tag is being published, make sure to deploy to the special
    # "stable" subdir as well
    deploy_docs_to = set([branch])
    if stable:
        if tag is not None:
            deploy_docs_to.add(tag)
        if latest:
            deploy_docs_to.add("master")
            deploy_docs_to.add("stable")

    # creates package directory, and then uploads directory there
    for k in deploy_docs_to:
        if not davclient.check(remote_path_prefix):  # base package directory
            logger.info("[dav] mkdir %s", remote_path_prefix)
            if not dry_run:
                davclient.mkdir(remote_path_prefix)
        remote_path = "%s/%s" % (remote_path_prefix, k)
        logger.info(
            "[dav] %s -> %s%s%s",
            path,
            _SERVER,
            server_info["root"],
            remote_path,
        )
        if not dry_run:
            davclient.upload_directory(local_path=path, remote_path=remote_path)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Deploys documentation from python-only packages"
    )
    parser.add_argument(
        "directory",
        help="Directory containing the sphinx build to deploy",
    )
    parser.add_argument(
        "-p",
        "--package",
        default=os.environ.get("CI_PROJECT_PATH", None),
        help="The package being built [default: %(default)s]",
    )
    parser.add_argument(
        "-x",
        "--visibility",
        default=os.environ.get("CI_PROJECT_VISIBILITY", "private"),
        help="The visibility of the package being built [default: %(default)s]",
    )
    parser.add_argument(
        "-b",
        "--branch",
        default=os.environ.get("CI_COMMIT_REF_NAME", None),
        help="Name of the branch being built [default: %(default)s]",
    )
    parser.add_argument(
        "-t",
        "--tag",
        default=os.environ.get("CI_COMMIT_TAG", None),
        help="If building a tag, pass it with this flag [default: %(default)s]",
    )
    parser.add_argument(
        "-u",
        "--username",
        default=os.environ.get("DOCUSER", None),
        help="Username for webdav deployment [default: %(default)s]",
    )
    parser.add_argument(
        "-P",
        "--password",
        default=os.environ.get("DOCPASS", None),
        help="Password for webdav deployment [default: %(default)s]",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose (enables INFO logging)",
        action="store_const",
        dest="loglevel",
        default=logging.WARNING,
        const=logging.INFO,
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    deploy_documentation(
        args.directory,
        package=args.package,
        stable=(args.tag is not None),
        latest=True,
        public=(args.visibility == "public"),
        branch=args.branch,
        tag=args.tag,
        username=args.username,
        password=args.password,
        dry_run=False,
    )
