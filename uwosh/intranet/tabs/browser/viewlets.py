from AccessControl import getSecurityManager
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter, getUtility
from zope.security import checkPermission
from uwosh.intranet.tabs.content import MemberTabsManager
from uwosh.intranet.tabs.interfaces import ITabs

class Tabs(ViewletBase):
    render = ViewPageTemplateFile('templates/tabs-viewlet.pt')

    def update(self):
        super(Tabs, self).update()
        self.tabs = MemberTabsManager(self.context).get_tabs_to_show()