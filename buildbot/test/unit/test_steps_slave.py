# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import stat
from twisted.trial import unittest
from buildbot.steps import slave
from buildbot.status.results import SUCCESS, FAILURE, EXCEPTION
from buildbot.process import properties
from buildbot.test.fake.remotecommand import Expect
from buildbot.test.util import steps, compat
from buildbot.interfaces import BuildSlaveTooOldError

class TestSetPropertiesFromEnv(steps.BuildStepMixin, unittest.TestCase):

    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def test_simple(self):
        self.setupStep(slave.SetPropertiesFromEnv(
                variables=["one", "two", "three", "five", "six"],
                source="me"))
        self.buildslave.slave_environ = { "one": "1", "two": None, "six": "6", "FIVE" : "555" }
        self.properties.setProperty("four", 4, "them")
        self.properties.setProperty("five", 5, "them")
        self.properties.setProperty("six", 99, "them")
        self.expectOutcome(result=SUCCESS,
                status_text=["SetPropertiesFromEnv"])
        self.expectProperty('one', "1", source='me')
        self.expectNoProperty('two')
        self.expectNoProperty('three')
        self.expectProperty('four', 4, source='them')
        self.expectProperty('five', 5, source='them')
        self.expectProperty('six', '6', source='me')
        self.expectLogfile("properties",
                "one = '1'\nsix = '6'")
        return self.runStep()

    def test_case_folding(self):
        self.setupStep(slave.SetPropertiesFromEnv(
                variables=["eNv"], source="me"))
        self.buildslave.slave_environ = { "ENV": 'EE' }
        self.buildslave.slave_system = 'win32'
        self.expectOutcome(result=SUCCESS,
                status_text=["SetPropertiesFromEnv"])
        self.expectProperty('eNv', 'EE', source='me')
        self.expectLogfile("properties",
                "eNv = 'EE'")
        return self.runStep()


class TestFileExists(steps.BuildStepMixin, unittest.TestCase):

    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def test_found(self):
        self.setupStep(slave.FileExists(file="x"))
        self.expectCommands(
            Expect('stat', { 'file' : 'x' })
            + Expect.update('stat', [stat.S_IFREG, 99, 99])
            + 0
        )
        self.expectOutcome(result=SUCCESS,
                status_text=["File found."])
        return self.runStep()

    def test_not_found(self):
        self.setupStep(slave.FileExists(file="x"))
        self.expectCommands(
            Expect('stat', { 'file' : 'x' })
            + Expect.update('stat', [0, 99, 99])
            + 0
        )
        self.expectOutcome(result=FAILURE,
                status_text=["Not a file."])
        return self.runStep()

    def test_failure(self):
        self.setupStep(slave.FileExists(file="x"))
        self.expectCommands(
            Expect('stat', { 'file' : 'x' })
            + 1
        )
        self.expectOutcome(result=FAILURE,
                status_text=["File not found."])
        return self.runStep()

    def test_render(self):
        self.setupStep(slave.FileExists(file=properties.Property("x")))
        self.properties.setProperty('x', 'XXX', 'here')
        self.expectCommands(
            Expect('stat', { 'file' : 'XXX' })
            + 1
        )
        self.expectOutcome(result=FAILURE,
                status_text=["File not found."])
        return self.runStep()

    @compat.usesFlushLoggedErrors
    def test_old_version(self):
        self.setupStep(slave.FileExists(file="x"),
                slave_version=dict())
        self.expectOutcome(result=EXCEPTION,
                status_text=["FileExists", "exception"])
        d = self.runStep()
        def check(_):
            self.assertEqual(
                    len(self.flushLoggedErrors(BuildSlaveTooOldError)), 1)
        d.addCallback(check)
        return d


class TestRemoveDirectory(steps.BuildStepMixin, unittest.TestCase):

    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def test_success(self):
        self.setupStep(slave.RemoveDirectory(dir="d"))
        self.expectCommands(
            Expect('rmdir', { 'dir' : 'd' })
            + 0
        )
        self.expectOutcome(result=SUCCESS,
                status_text=["RemoveDirectory"])
        return self.runStep()

    def test_failure(self):
        self.setupStep(slave.RemoveDirectory(dir="d"))
        self.expectCommands(
            Expect('rmdir', { 'dir' : 'd' })
            + 1
        )
        self.expectOutcome(result=FAILURE,
                status_text=["Delete failed."])
        return self.runStep()

    def test_render(self):
        self.setupStep(slave.RemoveDirectory(dir=properties.Property("x")))
        self.properties.setProperty('x', 'XXX', 'here')
        self.expectCommands(
            Expect('rmdir', { 'dir' : 'XXX' })
            + 0
        )
        self.expectOutcome(result=SUCCESS,
                status_text=["RemoveDirectory"])
        return self.runStep()

class TestMakeDirectory(steps.BuildStepMixin, unittest.TestCase):

    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def test_success(self):
        self.setupStep(slave.MakeDirectory(dir="d"))
        self.expectCommands(
            Expect('mkdir', { 'dir' : 'd' })
            + 0
        )
        self.expectOutcome(result=SUCCESS,
                status_text=["MakeDirectory"])
        return self.runStep()

    def test_failure(self):
        self.setupStep(slave.MakeDirectory(dir="d"))
        self.expectCommands(
            Expect('mkdir', { 'dir' : 'd' })
            + 1
        )
        self.expectOutcome(result=FAILURE,
                status_text=["Create failed."])
        return self.runStep()

    def test_render(self):
        self.setupStep(slave.MakeDirectory(dir=properties.Property("x")))
        self.properties.setProperty('x', 'XXX', 'here')
        self.expectCommands(
            Expect('mkdir', { 'dir' : 'XXX' })
            + 0
        )
        self.expectOutcome(result=SUCCESS,
                status_text=["MakeDirectory"])
        return self.runStep()
