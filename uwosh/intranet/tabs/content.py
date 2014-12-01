from Acquisition import aq_parent, Implicit
from AccessControl.Owned import Owned
from AccessControl.Role import RoleManager
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.Traversable import Traversable
from persistent import Persistent
from persistent.list import PersistentList
from Products.CMFCore.CMFCatalogAware import CatalogAware
from Products.CMFCore.CMFCatalogAware import WorkflowAware
from Products.CMFCore.DynamicType import DynamicType
from Products.CMFCore.utils import UniqueObject, getToolByName
from zope.component import getUtility
from zope.component.factory import Factory
from zope.container.ordered import OrderedContainer
from zope.interface import implements
from interfaces import ITab, ITabs
from utils import list_from_string, string_from_list

class Tabs(UniqueObject, Folder):
    implements(ITabs)

    meta_type = 'uwosh.intranet.tabs tool'
    id = 'tabs'
    
    def add_tab(self, tab):
        if ITab.providedBy(tab):
            id = tab.getId()
            setattr(self, id, tab)
            self._objects = self._objects + (
                {'id': id, 'meta_type': tab.meta_type},)
        else:
            raise Exception('Invalid tab type.')

    def remove_tab(self, id):
        try:
            index = self._objects.index({'id': id, 'meta_type': Tab.meta_type})
        except ValueError:
            raise Exception('The tab you are trying to remove, "%s", does not exist!' % id)
        self._objects = self._objects[:index] + self._objects[index+1:]
        delattr(self, id)
        
    def get_tab(self, id):
        return getattr(self, id, None)
        
    def get_tabs(self, ids):
        tabs = [self.get_tab(id) for id in ids]
        return filter(lambda t: t is not None, tabs)
        
    def get_all_tabs(self):
        return [obj for _, obj in self.objectItems()]

class MemberTabsManager(object):

    @property
    def portal_groups(self):
        return getToolByName(self.context, 'portal_groups')

    @property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')
    
    @property
    def tabs_tool(self):
        return getUtility(ITabs)
        
    def __init__(self, context, memberId=None):
        """
        If memberId is excluded the current authenticated member is used.
        """
        self.context = context
        if memberId:
            self.member = self.portal_membership.getMemberById(memberId)
        else:
            self.member = self.portal_membership.getAuthenticatedMember()
        if not self.member:
            raise Exception('Member "%s" does not exist.' % memberId)
            
    def get_tabs_to_show(self):
        added_tabs = set(list_from_string(self.member.getProperty('uwosh_intranet_tabs_added_tabs', '')))
        hidden_tabs = set(list_from_string(self.member.getProperty('uwosh_intranet_tabs_hidden_tabs', '')))
        groups = [self.portal_groups.getGroupById(id) for id in self.portal_groups.getGroupsForPrincipal(self.member)]
        suggested_tabs = set()
        for group in [g for g in groups if g]:
            suggested = list_from_string(group.getProperty('uwosh_intranet_tabs_suggested_tabs', ''))
            for tab in suggested:
                suggested_tabs.add(tab)            
        visible_tabs = (suggested_tabs - hidden_tabs) | added_tabs
        visible_tabs = sorted(list(visible_tabs))
        return self.tabs_tool.get_tabs(visible_tabs)
        
    def add_tab(self, tab_id):
        added_tabs = list_from_string(self.member.getProperty('uwosh_intranet_tabs_added_tabs', ''))
        if tab_id not in added_tabs:
            added_tabs.append(tab_id)
            self.member.setMemberProperties({'uwosh_intranet_tabs_added_tabs': string_from_list(added_tabs)})
    
    def hide_tab(self, tab_id):
        added_tabs = list_from_string(self.member.getProperty('uwosh_intranet_tabs_added_tabs', ''))
        hidden_tabs = list_from_string(self.member.getProperty('uwosh_intranet_tabs_hidden_tabs', ''))
        if tab_id in added_tabs:
            added_tabs.remove(tab_id)
        if tab_id not in hidden_tabs:
            hidden_tabs.append(tab_id)
        self.member.setMemberProperties({'uwosh_intranet_tabs_added_tabs': string_from_list(added_tabs),
                                         'uwosh_intranet_tabs_hidden_tabs': string_from_list(hidden_tabs)})
                                         
class GroupManager(object):
    def __init__(self, *args):
        if len(args) > 0:
            self.groups = args[0]
        else:
            self.groups = []
        
    def get_group(self, title):
        index = self._find_group_index(title)
        if index != -1:
            return self.groups[index]
        else:
            return None

    def _find_group_index(self, group_title):
        for i in range(0, len(self.groups)):
            if self.groups[i].title == group_title:
                return i
        return -1

    def __contains__(self, item):
        if type(item) in [str, unicode]:
            group = self.get_group(item)
            return group and True or False
        else:
            return item in self.groups

    def add_group(self, title):
        group = self.get_group(title)
        if group is not None:
            raise Exception('Group "%s" already exists.' % title)
        group = Group(title)
        self.groups.append(group)
        return group

    def rename_group(self, title, new_title):
        group = self.get_group(title)
        if group is None:
            raise Exception('Group "%s" does not exist.' % title)
        group.title = new_title

    def remove_group(self, group):
        group = self.get_group(group)
        if group is None:
            raise Exception('Group "%s" does not exist.' % group)
        self.groups.remove(group)

    def reorder_groups(self, order):
        """
        do this in much of the same way we do reordering of links
        """
        neworder = []
        oldorder = GroupManager(self.groups[:])
        for group in order:
            if group in oldorder:
                neworder.append(self.get_group(group))
                oldorder.remove_group(group)

        # add any leftover at the end
        neworder.extend(list(oldorder.groups))
        self.groups = PersistentList(neworder)

# XXX: we may want to extend PortalContent instead of some of these
class Tab(CatalogAware, WorkflowAware, DynamicType, Traversable,
          GroupManager, RoleManager, Owned, Implicit, Persistent, SimpleItem):
    """
    The main data structure for this class is self.groups. 
    It is currently just a list of Group objects.
    """
    implements(ITab)

    meta_type = 'Tab'
    portal_type = 'Tab'
    
    def __init__(self, *args, **kwargs):
        super(Tab, self).__init__(*args, **kwargs)
        self.groups = PersistentList()
        
    def Title(self):
        return self.title
        
    def getId(self):
        return self.id
    
class Group:
    def __init__(self, title):
        self.title = title
        self.links = PersistentList()

    def add_link(self, link):
        self.links.append(link)

    def remove_link(self, link):
        if link in self.links:
            self.links.remove(link)

    def reorder_links(self, order):
        # don't just do a blind re-assignment, reorder them with smarts :)
        neworder = []
        oldorder = self.links[:]
        for link in order:
            if link in oldorder:
                neworder.append(link)
                oldorder.remove(link)

        # add any leftover at the end
        neworder.extend(list(oldorder))
        self.links = PersistentList(neworder)
            
TabFactory = Factory(Tab)
