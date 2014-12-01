from plone.formwidget.contenttree import PathSourceBinder
from zope import schema
from zope.interface import Interface

class ILayer(Interface):
    """
    Marker interface that defines a browser layer
    """
    
class ITab(Interface):
    """
    """
    
    id = schema.TextLine(
        title=u'ID'
    )
    
    title = schema.TextLine(
        title=u'Title of tab.'
    )
    
    groups = schema.List(
        title=u'Groups of links',
        value_type=schema.Tuple(
            title=u'Title',
            value_type=schema.List(
                title=u'Object ids'
            )
        )
    )

class ILink(Interface):
    
    group = schema.TextLine(
        title=u'Group.',
        description=u'The group you are adding to.'
    )
    
    link = schema.Choice(
        title=u"Content Link",
        description=u"Find the piece of content which you'd like to link to.",
        required=True,
        source=PathSourceBinder(navigation_tree_query={
            'path': {'navtree': 0, 'query': u''}, 
            'portal_type': ['Document', 'Large Plone Folder', 'Event', 
                'File', 'Folder', 'Image', 'Link', 'News Item', 'Tab', 'Topic'], 
        })
    )
    
class IExternalLink(Interface):
    
    group = schema.TextLine(
        title=u'Group.',
        description=u'The group you are adding to.'
    )
    
    title = schema.TextLine(
        title=u'The title of the link.'
    )
    
    url = schema.URI(
        title=u'URL',
        default='http://'
    )
    
    
class IDeleteLink(Interface):

    group = schema.TextLine(
        title=u'Group.',
        description=u'The group you are adding to.'
    )

    link = schema.TextLine(title=u"Content Link")
    
class IGroup(Interface):
    """
    """

    name = schema.TextLine(
        title=u'Name'
    )

class IRenameGroup(IGroup):
    """
    """

    new_name = schema.TextLine(
        title=u'New Name'
    )
    
class ITabs(Interface):
    """
    """
    

    