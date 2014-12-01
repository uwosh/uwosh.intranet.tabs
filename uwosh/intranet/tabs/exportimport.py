from Products.CMFCore.utils import getToolByName
from content import Tabs

def install(context):
    if not context.readDataFile('uwosh.intranet.tabs.txt'):
        return
    site = context.getSite()
    setup = getToolByName(site, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-plone.formwidget.contenttree:default')
    setup.runAllImportStepsFromProfile('profile-plone.app.z3cform:default')
    addGroupDataProperties(site)
    
def addGroupDataProperties(site):    
    gdt = getToolByName(site, 'portal_groupdata')
    if not gdt.hasProperty('uwosh_intranet_tabs_suggested_tabs'):
        gdt.manage_addProperty('uwosh_intranet_tabs_suggested_tabs', '', 'string')