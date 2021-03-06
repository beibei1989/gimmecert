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


def test_status_on_uninitialised_directory(tmpdir):
    # John wants to see the status of current set of artefacts
    # generated by Gimmecert.

    # He swithces over to his project directory.
    tmpdir.chdir()

    # John runs the status command.
    stdout, stderr, exit_code = run_command('gimmecert', 'status')

    # It turns out that the directory has not been previously
    # initialised. In spite of this, the tool reports success, and
    # informs John that Gimmecert has not been initialised yet.
    assert exit_code == 0
    assert "CA hierarchy has not been initialised in current directory." in stdout


def test_status_on_initialised_directory(tmpdir):
    # John is interested in finding out a bit more about what
    # certificates have been already issued in one of the projects he
    # had initialised before.
    tmpdir.chdir()

    run_command('gimmecert', 'init', '-d', '3', '-b', 'My Project')

    run_command('gimmecert', 'server', 'myserver1')
    run_command('gimmecert', 'server', 'myserver2', 'myservice.example.com', 'myotherservice.example.com')
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myserver3.key.pem",
                "-subj", "/CN=myserver3", "-out", "myserver3.csr.pem")
    run_command('gimmecert', 'server', '--csr', 'myserver3.csr.pem', 'myserver3')

    run_command('gimmecert', 'client', 'myclient1')
    run_command('gimmecert', 'client', 'myclient2')
    run_command("openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", "myclient3.key.pem",
                "-subj", "/CN=myclient3", "-out", "myclient3.csr.pem")
    run_command('gimmecert', 'client', '--csr', 'myclient3.csr.pem', 'myclient3')

    # John switches to project directory.
    tmpdir.chdir()

    # John runs the status command.
    stdout, stderr, exit_code = run_command('gimmecert', 'status')
    stdout_lines = stdout.split("\n")

    # Command exits with success without any errors being
    # reported.
    assert exit_code == 0
    assert stderr == ""

    # John notices that information is laid-out in three separate
    # sections - one for CA hierachy, one for server certificates, and
    # one for client certificates.
    assert "CA hierarchy" in stdout
    assert "Server certificates" in stdout
    assert "Client certificates" in stdout

    # John first has a look at information about the CA
    # hierarchy. Hierarchy tree is presented using indentation. Each
    # CA is listed with its full subject DN, as well as not before and
    # not after dates. In addition, the final CA in chain is marked as
    # end entity issuing CA.
    index_ca_1 = stdout_lines.index("CN=My Project Level 1 CA")  # Should not raise
    index_ca_2 = stdout_lines.index("CN=My Project Level 2 CA")  # Should not raise
    index_ca_3 = stdout_lines.index("CN=My Project Level 3 CA [END ENTITY ISSUING CA]")  # Should not raise

    assert index_ca_1 < index_ca_2
    assert index_ca_2 < index_ca_3

    assert stdout_lines[index_ca_1+1].startswith("    Validity: ")
    assert stdout_lines[index_ca_1+2].startswith("    Certificate: ")

    assert stdout_lines[index_ca_2+1].startswith("    Validity: ")
    assert stdout_lines[index_ca_2+2].startswith("    Certificate: ")

    assert stdout_lines[index_ca_3+1].startswith("    Validity: ")
    assert stdout_lines[index_ca_3+2].startswith("    Certificate: ")

    # In addition to CA information, path to full certificate chain is
    # output as well.
    assert "Full certificate chain:" in stdout

    # John then has a look at server certificates. These are presented
    # in a list, and for each certificate is listed with subject DN,
    # not before, not after, and included DNS names. Information for
    # each server is followed by paths to private key and certificate.
    index_myserver1 = stdout_lines.index("CN=myserver1")  # Should not raise
    index_myserver2 = stdout_lines.index("CN=myserver2")  # Should not raise
    index_myserver3 = stdout_lines.index("CN=myserver3")  # Should not raise

    assert stdout_lines[index_myserver1+1].startswith("    Validity: ")
    assert stdout_lines[index_myserver1+2] == "    DNS: myserver1"
    assert stdout_lines[index_myserver1+3] == "    Private key: .gimmecert/server/myserver1.key.pem"
    assert stdout_lines[index_myserver1+4] == "    Certificate: .gimmecert/server/myserver1.cert.pem"

    assert stdout_lines[index_myserver2+1].startswith("    Validity: ")
    assert stdout_lines[index_myserver2+2] == "    DNS: myserver2, myservice.example.com, myotherservice.example.com"
    assert stdout_lines[index_myserver2+3] == "    Private key: .gimmecert/server/myserver2.key.pem"
    assert stdout_lines[index_myserver2+4] == "    Certificate: .gimmecert/server/myserver2.cert.pem"

    assert stdout_lines[index_myserver3+1].startswith("    Validity: ")
    assert stdout_lines[index_myserver3+2] == "    DNS: myserver3"
    assert stdout_lines[index_myserver3+3] == "    CSR: .gimmecert/server/myserver3.csr.pem"
    assert stdout_lines[index_myserver3+4] == "    Certificate: .gimmecert/server/myserver3.cert.pem"

    # For client certificates, John can see that for each certificate
    # he can see its subject DN and validity. Information for each
    # server is followed by paths to private key and certificate.
    index_myclient1 = stdout_lines.index("CN=myclient1")  # Should not raise
    index_myclient2 = stdout_lines.index("CN=myclient2")  # Should not raise
    index_myclient3 = stdout_lines.index("CN=myclient3")  # Should not raise

    assert stdout_lines[index_myclient1+1].startswith("    Validity: ")
    assert stdout_lines[index_myclient1+2] == "    Private key: .gimmecert/client/myclient1.key.pem"
    assert stdout_lines[index_myclient1+3] == "    Certificate: .gimmecert/client/myclient1.cert.pem"

    assert stdout_lines[index_myclient2+1].startswith("    Validity: ")
    assert stdout_lines[index_myclient2+2] == "    Private key: .gimmecert/client/myclient2.key.pem"
    assert stdout_lines[index_myclient2+3] == "    Certificate: .gimmecert/client/myclient2.cert.pem"

    assert stdout_lines[index_myclient3+1].startswith("    Validity: ")
    assert stdout_lines[index_myclient3+2] == "    CSR: .gimmecert/client/myclient3.csr.pem"
    assert stdout_lines[index_myclient3+3] == "    Certificate: .gimmecert/client/myclient3.cert.pem"
