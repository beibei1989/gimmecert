# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Branko Majic
#
# This file is part of Gimmecert.
#
# Gimmecert is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Gimmecert is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Gimmecert.  If not, see <http://www.gnu.org/licenses/>.
#


from .base import run_command


def test_status_command_available_with_help():
    # John has used Gimmecert for issuing server and client
    # certificates in one of his projects. Since the project has been
    # quite hectic, he has started to loose track of all the different
    # server and client certificates he has issued. He realises that
    # he needs to check what has been issued. Although this should be
    # possible by simply listing the directory content, John hopes
    # that there might be a convenience command for this instead that
    # provides some extra info as well. He starts off by running the
    # command without any paramrters to get a listing of available
    # commands.
    stdout, stderr, exit_code = run_command("gimmecert")

    # Looking at output, John notices the status command.
    assert exit_code == 0
    assert stderr == ""
    assert "status" in stdout

    # He goes ahead and has a look at command invocation to check what
    # kind of parameters he might need to provide.
    stdout, stderr, exit_code = run_command("gimmecert", "status", "-h")

    # John can see that the command does not take any additional
    # arguments.
    assert exit_code == 0
    assert stderr == ""
    assert stdout.split('\n')[0] == "usage: gimmecert status [-h]"
