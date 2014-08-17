from clients.http import make_nonprod_request as make_request
from nose.tools import with_setup
import test

STATE_SUCCESS = 1       # Response completed succesfully
STATE_FAILURE = 2       # Response failed due to user error
STATE_PANIC   = 3       # Response failed due to system error
STATE_AUTHERR = 4       # Response failed due to authentication error

# Utility functions
# Reset a list by deleting all items
def list_empty(tag):
    exist = make_request('list view %s' % tag)
    if exist['state'] == STATE_FAILURE:
        return

    for item in exist['data']:
        make_request(item[2]['Delete'])


@with_setup(test.setup_function, test.teardown_function)
def badinput_test():
    '''
    Test bad list item and tag data
    '''
    good = 'test'
    bad = [
        'test\'BAD\'HI',
        'test\"\"HI',
        'test\'',
        'test\"',
        'test+SPACE',
        'test%2fSPACE',
        'test\0',
        'test\0BAD',
        'test\nNEWLINE',
        'test\n',
        'test\n\r',
        'test\r\n',
        'test\\HI',
        'testHI\\',
        'test/HI',
        'test/HI/'
        'test#'
    ]

    # test each bad tag
    for b in bad:
        # check for empty list first
        list_empty(b)
        empty = make_request('list view %s' % b)
        assert empty['state'] == STATE_FAILURE
        empty = None

        newitem = make_request('list add %s %s' % (b, good))
        assert newitem['state'] == STATE_SUCCESS
        newitem = None

        # check new item exists
        exists = make_request('list view %s' % b)
        assert exists['state'] == STATE_SUCCESS
        assert len(exists['data']) == 1
        if exists['data'][0][0] != good:
            raise Exception(b)
        assert exists['data'][0][0] == good
        exists_delete = exists['data'][0][2]['Delete']
        exists = None

        # delete list item
        delete = make_request(exists_delete)
        assert delete['state'] == STATE_SUCCESS
        delete = None

        # check list is empty again
        empty2 = make_request('list view %s' % b)
        assert empty2['state'] == STATE_FAILURE
        empty2 = None

@with_setup(test.setup_function, test.teardown_function)
def list_adddeleteitem_test():
    '''
    Test adding and deleting list items
    '''
    tag = 'UNITTESTLIST'
    listitem = 'test list item'

    # check for empty list first
    list_empty(tag)
    empty = make_request('list view %s' % tag)
    assert empty['state'] == STATE_FAILURE
    assert empty['write'] == False
    empty = None

    # add new item
    newitem = make_request('list add %s %s' % (tag, listitem))
    assert newitem['state'] == STATE_SUCCESS
    assert newitem['write'] == True
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists_delete = exists['data'][0][2]['Delete']
    exists = None

    # delete list item
    delete = make_request(exists_delete)
    assert delete['state'] == STATE_SUCCESS
    assert delete['write'] == True
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag)
    assert empty2['state'] == STATE_FAILURE
    empty2 = None

@with_setup(test.setup_function, test.teardown_function)
def list_adddeletetags_test():
    '''
    Test adding and removing tags from list items
    '''
    tag = 'UNITTESTTAG1'
    tag2 = 'UNITTESTTAG2'
    listitem = 'test list tag item'

    # check for empty lists first
    list_empty(tag)
    list_empty(tag2)

    # add new item with first tag
    newitem = make_request('list add %s %s' % (tag, listitem))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    existsid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # add second tag
    newtag = make_request('list tag %s %s' % (existsid, tag2))
    assert newtag['state'] == STATE_SUCCESS
    newtag = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = make_request('list view %s' % tag2)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

    # delete list item
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == STATE_SUCCESS
    assert len(delete['data']) == 2
    assert delete['data'][0][0] == 'View list "%s"' % tag
    assert delete['data'][1][0] == 'View list "%s"' % tag2
    delete = None

    # already deleted
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == STATE_FAILURE
    delete = None

    delete = make_request('list remove %s %s' % (tag2, existsid))
    assert delete['state'] == STATE_SUCCESS
    assert len(delete['data']) == 1
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag)
    assert empty2['state'] == STATE_FAILURE
    empty2 = make_request('list view %s' % tag2)
    assert empty2['state'] == STATE_FAILURE
    empty2 = None

@with_setup(test.setup_function, test.teardown_function)
def list_adddeletetags_test():
    '''
    Check adding the same tag twice to a list item doesn't make
    it appear twice, or need to be deleted twice
    '''
    tag = 'UNITTESTTAGSDOUBLEUP'
    listitem = 'test list tag item'

    # check for empty lists first
    list_empty(tag)

    # add new item with first tag
    newitem = make_request('list add %s %s' % (tag, listitem))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    existsid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # add same tag again
    newtag = make_request('list tag %s %s' % (existsid, tag))
    assert newtag['state'] == STATE_SUCCESS
    newtag = None

    # check item only shows once
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

    # delete list item
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == STATE_SUCCESS
    assert len(delete['data']) == 1
    assert delete['data'][0][0] == 'View list "%s"' % tag
    delete = None

    # check it no longer appears
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == STATE_FAILURE
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag)
    assert empty2['state'] == STATE_FAILURE
    empty2 = None


@with_setup(test.setup_function, test.teardown_function)
def list_itemorder_basic_test():
    '''
    Check items appear in order added when displayed
    '''
    tag = 'UNITTESTLISTORDER'
    listitem = 'test list item item#'

    # check for empty lists first
    list_empty(tag)

    # add four new items
    for i in range(0, 4):
        newitem = make_request('list add %s %s' % (tag, '%s%d' % (listitem, i)))
        assert newitem['state'] == STATE_SUCCESS
        newitem = None

    # check four items exist
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 4

    # check they are in the same order we added them
    e = 0
    for i in range(0, 4):
        assert exists['data'][e][0] == '%s%d' % (listitem, i)
        e += 1

    exists = None

    list_empty(tag)


@with_setup(test.setup_function, test.teardown_function)
def list_itemorder_multitag_test():
    '''
    Check items appear in order tags added when displayed
    '''
    tag = 'UNITTESTLISTORDERTAG'
    tagalt = 'UNITTESTLISTORDERTAGALT'
    listitem = 'test list item item#'

    # check for empty lists first
    list_empty(tag)
    list_empty(tagalt)

    # add item to alternate list first
    newitem = make_request('list add %s %s' % (tagalt, '%s%d' % (listitem, 9)))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    exists = make_request('list view %s' % tagalt)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    altitemid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # add two new items to correct tag
    for i in range(0, 2):
        newitem = make_request('list add %s %s' % (tag, '%s%d' % (listitem, i)))
        assert newitem['state'] == STATE_SUCCESS
        newitem = None

    # check two items exist
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 2
    exists = None

    # add tag to alternate item, adding it to the *end* of this list
    newitem = make_request('list tag %s %s' % (altitemid, tag))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # check three items exist
    exists = make_request('list view %s' % tag)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 3

    # check they are in the same order we added the tags
    # this means that the alternate item should be last on the list
    expect = [0, 1, 9]
    e = 0
    for i in expect:
        assert exists['data'][e][0] == '%s%d' % (listitem, i)
        e += 1

    exists = None

    list_empty(tag)
    list_empty(tagalt)


@with_setup(test.setup_function, test.teardown_function)
def list_missingtag_test():
    '''
    Test handling of empty tags
    '''
    newitem = make_request('list add  item')
    assert newitem['state'] == STATE_FAILURE
    assert newitem['message'] == 'No tag specified'
    newitem = None

    newitem = make_request('list tag 1 ')
    assert newitem['state'] == STATE_FAILURE
    assert newitem['message'] == 'No tag specified'
    newitem = None


@with_setup(test.setup_function, test.teardown_function)
def list_move_test():
    '''
    Test the list move action
    '''
    tag_origin = 'UNITTESTORIGIN'
    tag_dest = 'UNITTESTDESTINATION'
    listitem = 'tagitem'

    # check for empty lists first
    list_empty(tag_origin)
    list_empty(tag_dest)

    # add new item with first tag
    newitem = make_request('list add %s %s' % (tag_origin, listitem))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag_origin)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    existsid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # fail to move item from wrong tag
    wrongtag = make_request('list move %s %s %s' % (existsid, 'UNITESTNONEXISTANTTAG', tag_dest))
    assert wrongtag['state'] == STATE_FAILURE
    wrongtag = None

    # move item to new tag
    newtag = make_request('list move %s %s %s' % (existsid, tag_origin, tag_dest))
    assert newtag['state'] == STATE_SUCCESS
    newtag = None

    # check item only shows once
    exists = make_request('list view %s' % tag_dest)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

    # check it no longer appears at old tag
    old = make_request('list view %s' % (tag_origin))
    assert old['state'] == STATE_FAILURE
    old = None

    # delete list item
    delete = make_request('list remove %s %s' % (tag_dest, existsid))
    assert delete['state'] == STATE_SUCCESS
    assert len(delete['data']) == 1
    assert delete['data'][0][0] == 'View list "%s"' % tag_dest
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag_origin)
    assert empty2['state'] == STATE_FAILURE
    empty2 = None

    # check list is empty again
    empty3 = make_request('list view %s' % tag_dest)
    assert empty3['state'] == STATE_FAILURE
    empty3 = None


@with_setup(test.setup_function, test.teardown_function)
def list_multipletagview_test():
    '''
    Test the list view with multiple tags
    '''
    tag_one = 'UNITTESTTAG1'
    tag_two = 'UNITTESTTAG2'
    listitem = 'tagitemtwotags'
    listitemsingle = 'tagitemonetag'

    # check for empty lists first
    list_empty(tag_one)
    list_empty(tag_two)

    # add new item with first tag
    newitem = make_request('list add %s %s' % (tag_one, listitem))
    assert newitem['state'] == STATE_SUCCESS
    itemid = newitem['data'][0][2]['Delete'].split(' ')[3]
    newitem = None

    # add new item with first tag
    newitem = make_request('list add %s %s' % (tag_one, listitemsingle))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # add new item with second tag
    newitem = make_request('list add %s %s' % (tag_two, listitemsingle))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # add second tag to first item
    newitem = make_request('list tag %s %s' % (itemid, tag_two))
    assert newitem['state'] == STATE_SUCCESS
    newitem = None

    # check two items in first tag
    exists = make_request('list view %s' % tag_one)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 2
    exists = None

    # check one item in second tag
    exists = make_request('list view %s' % tag_two)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 2
    exists = None

    # check one item when loading both tags!
    exists = make_request('list view %s %s' % (tag_one, tag_two))
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

@with_setup(test.setup_function, test.teardown_function)
def list_addmoveitem_test():
    '''
    Test adding and moving list items
    '''
    tag1 = 'TestTag1'
    tag2 = 'TestTag2'
    listitem = 'test list item'

    # check for empty lists first
    list_empty(tag1)
    list_empty(tag2)

    # Add new item
    newitem = make_request('list add %s %s' % (tag1, listitem))
    assert newitem['state'] == STATE_SUCCESS
    assert newitem['write'] == True
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag1)
    assert exists['state'] == STATE_SUCCESS
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists_delete = exists['data'][0][2]['Delete']
    itemid = exists['data'][0][3]['id']
    exists = None

    # Move new item
    move = make_request('list move %s %s %s' % (itemid, tag1, tag2))
    assert move['state'] == STATE_SUCCESS
    assert len(move['data']) == 1
    assert move['data'][0][0] == listitem

    # Check to see if tag1 list is empty
    empty = make_request('list view %s' % tag1)
    assert empty['state'] == STATE_FAILURE

    # Make sure item is in list 2
    moved = make_request('list view %s' % tag2)
    assert moved['state'] == STATE_SUCCESS
    assert len(moved['data']) == 1
    assert moved['data'][0][0] == listitem
