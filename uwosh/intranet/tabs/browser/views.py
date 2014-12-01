from os.path import join
from urllib import urlencode
from plone.formwidget.contenttree import ContentTreeFieldWidget
from plone.memoize.instance import memoize
from plone.z3cform import layout
from plone.z3cform.layout import wrap_form, FormWrapper
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from z3c.form import form, field, button
from z3c.form.interfaces import INPUT_MODE, HIDDEN_MODE, DISPLAY_MODE
from zope.component import createObject, getMultiAdapter, getUtility
import zope.event
from zope.security import checkPermission
from uwosh.intranet.tabs.interfaces import ITab, ITabs, IGroup, ILink, \
    IDeleteLink, IExternalLink, IRenameGroup
from uwosh.intranet.tabs.utils import generate_unique_id
from uwosh.intranet.tabs.content import MemberTabsManager

class AddTab(form.AddForm):
    fields = field.Fields(ITab).omit('id', 'groups')

    label = u'Add tab'

    @button.buttonAndHandler(u'Add')
    def handleApply(self, action):
        data, errors = self.extractData()
        if not errors:
            tabs = getUtility(ITabs)
            tab = createObject('tab.TabFactory')
            tab.title = data['title']
            tab.id = generate_unique_id(tabs.objectIds(), tab.title)
            tabs.add_tab(tab)
        
            self.request.response.redirect(self.context.absolute_url() + '/' + tab.id)

class AddGroup(form.AddForm):
    fields = field.Fields(IGroup)
    
    label = u'Add group'
    
    @button.buttonAndHandler(u'Add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if not errors:
            groupName = data['name']
            self.context.add_group(groupName)
            self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

class RenameGroup(form.AddForm):
    fields = field.Fields(IRenameGroup)
    
    @property
    def group(self):
        return self.request.get('group', self.request.get('form.widgets.name'))

    def updateWidgets(self):
        super(RenameGroup, self).updateWidgets()
        self.widgets['name'].mode = HIDDEN_MODE
        self.widgets['name'].value = self.group

        self.label = u'Rename %s' % self.group

    @button.buttonAndHandler(u'Rename')
    def handleRename(self, action):
        data, errors = self.extractData()
        if not errors:
            group = data['name']
            new_name = data['new_name']
            self.context.rename_group(group, new_name)
            self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        data, errors = self.extractData()
        self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')
        
class AddExternalLink(form.AddForm):
    fields = field.Fields(IExternalLink)

    def updateWidgets(self):
        super(AddExternalLink, self).updateWidgets()
        self.widgets['group'].mode = HIDDEN_MODE
        self.widgets['group'].value = self.request.get('group', 
            self.request.get('form.widgets.group'))
            
    @button.buttonAndHandler(u'Add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if not errors:
            group = data['group']
            title = data['title']
            url = data['url']
            portal_state = getMultiAdapter((self.context, self.request), 
                                                name=u'plone_portal_state')

            portal = portal_state.portal()
            id = portal.invokeFactory('Link', portal.generateUniqueId(), 
                title=title, remoteUrl=url)
            link = portal[id]
            zope.event.notify(ObjectInitializedEvent(link))
            
            workflow_tool = getToolByName(portal, 'portal_workflow')
            workflow_tool.doActionFor(link, 'publish')
            link.reindexObject()
            
            group = self.context.get_group(group)
            group.add_link(link.UID())
            self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

class AddLink(form.AddForm):
    fields = field.Fields(ILink)
    fields['link'].widgetFactory = ContentTreeFieldWidget
    
    def updateWidgets(self):
        super(AddLink, self).updateWidgets()
        self.widgets['group'].mode = HIDDEN_MODE
        self.widgets['group'].value = self.request.get('group', 
            self.request.get('form.widgets.group'))
    
    @button.buttonAndHandler(u'Add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if not errors:
            group = data['group']
            link = data['link']
            portal_state = getMultiAdapter((self.context, self.request), 
                                                name=u'plone_portal_state')
            portal_path = '/'.join(portal_state.portal().getPhysicalPath())
            link = join(portal_path, self.request.get('link').lstrip('/'))
            link = self.context.restrictedTraverse(link)
            
            group = self.context.get_group(group)
            group.add_link(link.UID())
            self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

class AllTabsView(BrowserView):
    template = ViewPageTemplateFile('templates/all-tabs-view.pt')
    
    def __call__(self):
        return self.template()      

    @property
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')

    @property
    def allTabs(self):
        return getUtility(ITabs).get_all_tabs()
    
    @property
    def myTabs(self):
        return MemberTabsManager(self.context).get_tabs_to_show()
    
    @property
    def canManageTabs(self):
        return checkPermission('uwosh.intranet.tabs.ManageTabs', self.context)
        
class AddToMyTabs(BrowserView):
    
    def __call__(self):
        tab_id = self.request.get('tab', '')
        if tab_id:
            MemberTabsManager(self.context).add_tab(tab_id)
        self.request.response.redirect(self.context.absolute_url() + '/@@all-tabs')

class RemoveFromMyTabs(BrowserView):
    
    def __call__(self):
        tab_id = self.request.get('tab', '')
        if tab_id:
            MemberTabsManager(self.context).hide_tab(tab_id)
        self.request.response.redirect(self.context.absolute_url() + '/@@all-tabs')
        
class TabBaseView(BrowserView):
  
    def __init__(self, context, request):
        super(TabBaseView, self).__init__(context, request)
        # have to use portal catalog because uid_catalog is not 
        # security aware unfortunately... 
        # we'll have to monitor performance...
        self.catalog = getToolByName(self.context, 'portal_catalog')
  
    def groups(self):
        return self.context.groups
         
    def get_links(self, uids):
        """
        This should filter bad links since it's a catalog search...
        """
        links = list(self.catalog(UID=list(uids)))
        #return them ordered...
        for uid in uids:
            for index in range(len(links)):
                if links[index].UID == uid:
                    yield links.pop(index)
                    break
        
    def encode(self, **kwargs):
        return urlencode(kwargs)
      
class TabView(TabBaseView):
    template = ViewPageTemplateFile('templates/tab-view.pt')
    
    def __call__(self):
        return self.template()
      
class ManageGroupsView(TabBaseView):
    template = ViewPageTemplateFile('templates/manage-groups-view.pt')
    
    recent_query = {
        'sort_on' : 'modified',
        'sort_order' : 'reverse',
        'sort_limit' : 10
    }
    
    def __call__(self):
        return self.template()

    def recent_items(self):
        return self.catalog(**self.recent_query)[:10]
        
    def recent_by_user_items(self):
        q = self.recent_query.copy()
        ps = getMultiAdapter((self.context, self.request), 
                                        name=u'plone_portal_state')
        member = ps.member()
        q['Creator'] = member.getId()
        return self.catalog(**q)[:10]

    def update_link_order(self):
        group_id = self.request.get('groupId', '')
        links_order = self.request.get('order[]', [])
        if not all((group_id, links_order)):
            return
        group = self.context.get_group(group_id)
        group.reorder_links(links_order)
    
    def update_group_order(self):
        group_order = self.request.get('order[]', [])
        if not group_order:
            return
        self.context.reorder_groups(group_order)

class DeleteLink(form.AddForm):
    # use a different set of fields since the ILink's value type doesn't work
    # correctly with hidden values
    fields = field.Fields(IDeleteLink)

    @property
    def link(self):
        return self.request.get('link', self.request.get('form.widgets.link'))

    @property
    def group(self):
        return self.request.get('group', self.request.get('form.widgets.group'))

    def updateWidgets(self):
        super(DeleteLink, self).updateWidgets()
        self.widgets['group'].mode = HIDDEN_MODE
        self.widgets['group'].value = self.group
        self.widgets['link'].mode = HIDDEN_MODE
        self.widgets['link'].value = self.link

        catalog = getToolByName(self.context, 'portal_catalog')
        link = catalog(UID=self.link)[0]
        
        self.label = u'Delete %s' % link.Title
        
        self.status = u"Are you sure you want to delete '%s' from the group '%s'" % (
            link.Title,
            self.group
        )       

    @button.buttonAndHandler(u'Delete')
    def handleDelete(self, action):
        data, errors = self.extractData()
        if not errors:
            group = data['group']
            link = data['link']
            
            group = self.context.get_group(group)
            group.remove_link(link)
            self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')
            
    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        data, errors = self.extractData()
        self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

class DeleteGroup(form.AddForm):
    fields = field.Fields(IGroup)

    @property
    def group(self):
        return self.request.get('group', self.request.get('form.widgets.name'))

    def updateWidgets(self):
        super(DeleteGroup, self).updateWidgets()
        self.widgets['name'].mode = HIDDEN_MODE
        self.widgets['name'].value = self.group

        self.label = u'Delete %s' % self.group

        self.status = u"Are you sure you want to the group '%s'" % (
            self.group
        )

    @button.buttonAndHandler(u'Delete')
    def handleDelete(self, action):
        data, errors = self.extractData()
        if not errors:
            group = data['name']
            self.context.remove_group(group)
            self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        data, errors = self.extractData()
        self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

class NavigationGenerator(BrowserView):
    """
    A little weird in doing this since we have to make everything from the 
    plone site look like it's at the root even thought it's not really
    at the root of the zope.
    
    So it'll come in like,
    
        /a-folder
        
    which means
    
        /Plone/a-folder
        
    and on the way out we translate sub-item to..
    
        /a-folder/item1
        /a-folder/item2
        ...
    
    """
    
    klass_mapping = {
        'Large Plone Folder' : 'directory',
        'Folder' : 'directory',
        'File' : 'file',
        'Document' : 'file ext_html',
        'Event' : 'file html',
        'Topic' : 'file ext_sql',
        'News Item' : 'file ext_html',
        'Image' : 'file ext_jpg',
        'default' : 'file'
    }
    
    def __call__(self):
        obj = self.context.unrestrictedTraverse(self.path)
        objpath = obj.getPhysicalPath()
        query = {
            'path': {
                'navtree': 1, 
                'query': '/'.join(objpath), 
                'navtree_start': (len(objpath) - len(self.portal_path)) + 1
            }, 
            'sort_on': 'getObjPositionInParent', 
            'sort_order': 'asc'
        }
        catalog = getToolByName(self.context, 'portal_catalog')
        return self.build_html(catalog(**query))
        
    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), 
                                        name=u'plone_portal_state')
     
    @property
    @memoize
    def portal_path(self):
        return self.portal_state.portal().getPhysicalPath()
        
    @property
    @memoize
    def path(self):
        path = self.request.get('dir', '/')
        portal_path = '/'.join(self.portal_path)
        return join(portal_path, path.lstrip('/')).rstrip('/')
        
    def build_html(self, items):
        html = """<ul class="jqueryFileTree" style="display: none;">"""
        for item in items:
            pt = item.portal_type
            klass = self.klass_mapping.has_key(pt) and self.klass_mapping[pt] or self.klass_mapping['default']
            #try the portal path off the path
            path = item.getPath().split('/')[len(self.portal_path):]
            path = '/'.join(path)
            if pt == "Folder":
                path = path + '/'
            html += """<li class="%s collapsed"><a href="#" rel="%s">%s</a></li>""" % (
                klass,
                path,
                item.Title
            )
        html += "</ul>"
        
        return html
        
    def ajax_add_link(self):
        group = self.request.get('group')
        link = self.request.get('link')
        _type = self.request.get('type')
        if _type == 'path':
            link = join('/'.join(self.portal_path), link)
            link = self.context.restrictedTraverse(link).UID()
            
        group = self.context.get_group(group)
        group.add_link(link)        
        self.request.response.redirect(self.context.absolute_url() + '/@@manage-groups')

class Search(BrowserView):
    
    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        res = catalog(SearchableText=self.request.get('q'))
        res = '\n'.join([b.Title + '|' + b.UID + '|' + b.Description for b in res])
        return res

AddTabForm = wrap_form(AddTab)
AddGroupForm = wrap_form(AddGroup)
AddLinkForm = wrap_form(AddLink)
RenameGroupForm = wrap_form(RenameGroup)
DeleteLinkForm = wrap_form(DeleteLink)
DeleteGroupForm = wrap_form(DeleteGroup)
AddExternalLinkForm = wrap_form(AddExternalLink)