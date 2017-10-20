from __future__ import print_function
from release_ccharp.utils import lazyprop
from release_ccharp.exceptions import SnpseqReleaseException
from release_tools.workflow import Conventions


class BranchProvider:
    """
    A wrapper of the release-tools Workflow class
    providing convenience methods
    """
    def __init__(self, workflow):
        self.workflow = workflow

    @lazyprop
    def latest_version(self):
        return self.workflow.get_latest_version()

    @lazyprop
    def candidate_branch(self):
        queue = self.workflow.get_queue()
        if len(queue) == 0:
            raise SnpseqReleaseException("There is no new candidate branch")
        return queue[0]

    @lazyprop
    def candidate_version(self):
        tag = Conventions.get_tag_from_branch(self.candidate_branch)
        return Conventions.get_version_from_tag(tag)

