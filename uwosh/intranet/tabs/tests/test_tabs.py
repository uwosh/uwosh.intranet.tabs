import unittest2 as unittest

from plone.app.testing import PLONE_INTEGRATION_TESTING, TEST_USER_NAME, \
    login, ploneSite, quickInstallProduct

from layer import INTEGRATION_TAB_TESTING

class TestTabs(unittest.TestCase):

    layer = INTEGRATION_TAB_TESTING

    def test_reorder_links(self):
        with ploneSite() as portal:
            tabs = portal.tabs
            tab1 = tabs['tab-1']
            
            group = tab1.get_group('group-1')
            links = group.links[:]
            tmp = links[0]
            links[0] = links[1]
            links[1] = tmp
            
            group.reorder_links(links)
            
            self.assertEquals(group.links[0], links[0])
            self.assertEquals(group.links[1], links[1])
            self.assertEquals(group.links[2], links[2])
            
    def test_reorder_links_does_not_lose_items(self):
        with ploneSite() as portal:
            tabs = portal.tabs
            tab1 = tabs['tab-1']
            
            group = tab1.get_group('group-1')
            links = group.links[:]
            
            group.reorder_links([None, None, None])
            
            self.assertTrue(links[0] in group.links)
            self.assertTrue(links[1] in group.links)
            self.assertTrue(links[2] in group.links)
        
    def test_reorder_groups(self):
        with ploneSite() as portal:
            tabs = portal.tabs
            tab1 = tabs['tab-1']
            
            tab1.reorder_groups(['group-2', 'group-1'])
                        
            self.assertEquals(tab1.groups[0].title, 'group-2')
            self.assertEquals(tab1.groups[1].title, 'group-1')
        
    def test_reorder_groups_does_not_lose_groups(self):
        with ploneSite() as portal:
            tabs = portal.tabs
            tab1 = tabs['tab-1']
            orig_groups = tab1.groups[:]

            tab1.reorder_groups([5, 'a group that does not exist'])
            
            self.assertEquals(tab1.groups[0].title, orig_groups[0].title)
            self.assertEquals(tab1.groups[1].title, orig_groups[1].title)
        
        