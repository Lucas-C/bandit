# -*- coding:utf-8 -*-
#
# Copyright 2016 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ast
import fnmatch

from bandit.core import extension_loader
from bandit.core import issue


def report_issue(check, name):
    return issue.Issue(
        severity=check['level'], confidence='HIGH',
        text=check['message'].replace('{name}', name),
        ident=name, test_id=check["id"])


def blacklist(context):
    blacklists = extension_loader.MANAGER.blacklist
    node_type = context.node.__class__.__name__
    if node_type not in blacklists:
        return

    if node_type == 'Call':
        func = context.node.func
        if isinstance(func, ast.Name) and func.id == '__import__':
            if len(context.node.args):
                name = context.node.args[0].s
            else:
                name = ""  # handle '__import__()'
        else:
            name = context.call_function_name_qual
        for check in blacklists[node_type]:
            for qn in check['qualnames']:
                if fnmatch.fnmatch(name, qn):
                    return report_issue(check, name)

    if node_type.startswith('Import'):
        prefix = ""
        if node_type == "ImportFrom":
            if context.node.module is not None:
                prefix = context.node.module + "."

        for check in blacklists[node_type]:
            for name in context.node.names:
                for qn in check['qualnames']:
                    if (prefix + name.name).startswith(qn):
                        return report_issue(check, name.name)