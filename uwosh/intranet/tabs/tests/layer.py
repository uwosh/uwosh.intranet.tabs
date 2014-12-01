from plone.testing import Layer
from plone.testing import z2

from plone.app.testing import PLONE_INTEGRATION_TESTING, TEST_USER_NAME, \
    PLONE_FIXTURE, login, ploneSite, quickInstallProduct, IntegrationTesting, \
    PloneSandboxLayer, applyProfile

from uwosh.intranet.tabs.content import Tab, Group
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig

class TabFixture(PloneSandboxLayer):
    defaultBases = (PLONE_INTEGRATION_TESTING,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import uwosh.intranet.tabs
        xmlconfig.file('configure.zcml', uwosh.intranet.tabs, context=configurationContext)
        z2.installProduct(app, 'uwosh.intranet.tabs')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'uwosh.intranet.tabs:default')
        
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser('user1', 'secret', ['Manager'], [])
        login(portal, 'user1')
        page1 = portal[portal.invokeFactory('Document', 'page-1', title=u"Page 1")]
        page2 = portal[portal.invokeFactory('Document', 'page-2', title=u"Page 2")]
        folder1 = portal[portal.invokeFactory('Folder', 'folder-1', title=u"Folder 1")]
        folder2 = portal[portal.invokeFactory('Folder', 'folder-2', title=u"Folder 2")]
        news1 = portal[portal.invokeFactory('News Item', 'news-item-1', title=u"News Item 1")]
        news2 = portal[portal.invokeFactory('News Item', 'news-item-2', title=u"News Item 2")]
    
        tabs = portal.tabs
        tab1 = Tab()
        tab1.id = tab1.title = 'tab-1'
        group1 = tab1.add_group('group-1')
        group1.links.extend([page1.UID(), page2.UID(), folder1.UID()])
        group2 = tab1.add_group('group-2')
        group2.links.extend([folder2.UID(), news1.UID(), news2.UID()])
    
        tabs.add_tab(tab1)
        tab2 = Tab()
        tab2.id = tab2.title = 'tab-2'
        tabs.add_tab(tab2)

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'uwosh.intranet.tabs')


TAB_FIXTURE = TabFixture()
INTEGRATION_TAB_TESTING = IntegrationTesting(bases=(TAB_FIXTURE,), name='INTEGRATION_TAB_TESTING')