from clients.http import make_request


def list_empty(tag):
    exist = make_request('list view %s' % tag)
    if exist['state'] == 2:
        return

    for item in exist['data']:
        make_request(item[2]['Delete'])


def authpositive_test():
    '''
    Check a positive auth works
    '''
    positive = make_request('server connect')
    assert positive['state'] == 1
    assert len(positive['data']) > 0

def authnegative_test():
    '''
    Test that a failed auth does indeed fail
    '''
    negative = make_request('server connect', 'badsecret')
    assert negative['state'] == 4
    assert negative['data'] == [[[]]]

def weather_test():
    '''
    Test home page shows weather
    '''
    weather = make_request('server connect')
    assert weather['data'][0][0].startswith('Today')
    assert weather['data'][1][0].startswith('Tomorrow')

def badpath_test():
    '''
    Test a non existant function or action fails correctly
    '''
    yes = make_request('server connect')
    assert yes['state'] == 1
    yes = None

    nofunc = make_request('notreal connect')
    assert nofunc['state'] == 2
    assert nofunc['message'] == 'ERROR: Function does not exist'
    nofunc = None

    noact = make_request('server notreal')
    assert noact['state'] == 2
    assert noact['message'] == 'ERROR: Action does not exist'
    noact = None

def badinput_test():
    '''
    Test bad list item and tag data
    '''
    good = 'UNITTESTLISTBAD'
    bad = [
        'UNITTESTLISTBAD\'BAD\'HI',
        'UNITTESTLISTBAD\"\"HI',
        'UNITTESTLISTBAD\'',
        'UNITTESTLISTBAD\"',
        'UNITTESTLISTBAD+SPACE',
        'UNITTESTLISTBAD%2fSPACE',
        'UNITTESTLISTBAD\0',
        'UNITTESTLISTBAD\0BAD',
        'UNITTESTLISTBAD\nNEWLINE',
        'UNITTESTLISTBAD\n',
        'UNITTESTLISTBAD\n\r',
        'UNITTESTLISTBAD\r\n',
        'UNITTESTLISTBAD\\HI',
        'UNITTESTLISTBADHI\\',
        'UNITTESTLISTBAD/HI',
        'UNITTESTLISTBAD/HI/'
        'UNITTESTLISTBAD#'
    ]

    # test each bad tag
    for b in bad:
        # check for empty list first
        list_empty(b)
        empty = make_request('list view %s' % b)
        assert empty['state'] == 2
        empty = None

        newitem = make_request('list add %s %s' % (b, good))
        assert newitem['state'] == 1
        newitem = None

        # check new item exists
        exists = make_request('list view %s' % b)
        assert exists['state'] == 1
        assert len(exists['data']) == 1
        if exists['data'][0][0] != good:
            raise Exception(b)
        assert exists['data'][0][0] == good
        exists_delete = exists['data'][0][2]['Delete']
        exists = None

        # delete list item
        delete = make_request(exists_delete)
        assert delete['state'] == 1
        delete = None

        # check list is empty again
        empty2 = make_request('list view %s' % b)
        assert empty2['state'] == 2
        empty2 = None

def list_adddeleteitem_test():
    '''
    Test adding and deleting list items
    '''
    tag = 'UNITTESTLIST'
    listitem = 'test list item'

    # check for empty list first
    list_empty(tag)
    empty = make_request('list view %s' % tag)
    assert empty['state'] == 2
    assert empty['write'] == 0
    empty = None

    # add new item
    newitem = make_request('list add %s %s' % (tag, listitem))
    assert newitem['state'] == 1
    assert newitem['write'] == 1
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists_delete = exists['data'][0][2]['Delete']
    exists = None

    # delete list item
    delete = make_request(exists_delete)
    assert delete['state'] == 1
    assert delete['write'] == 1
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag)
    assert empty2['state'] == 2
    empty2 = None

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
    assert newitem['state'] == 1
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    existsid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # add second tag
    newtag = make_request('list tag %s %s' % (existsid, tag2))
    assert newtag['state'] == 1
    newtag = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = make_request('list view %s' % tag2)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

    # delete list item
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == 1
    assert len(delete['data']) == 2
    assert delete['data'][0][0] == 'View list "%s"' % tag
    assert delete['data'][1][0] == 'View list "%s"' % tag2
    delete = None

    # already deleted
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == 2
    delete = None

    delete = make_request('list remove %s %s' % (tag2, existsid))
    assert delete['state'] == 1
    assert len(delete['data']) == 1
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag)
    assert empty2['state'] == 2
    empty2 = make_request('list view %s' % tag2)
    assert empty2['state'] == 2
    empty2 = None


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
    assert newitem['state'] == 1
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    existsid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # add same tag again
    newtag = make_request('list tag %s %s' % (existsid, tag))
    assert newtag['state'] == 1
    newtag = None

    # check item only shows once
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

    # delete list item
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == 1
    assert len(delete['data']) == 1
    assert delete['data'][0][0] == 'View list "%s"' % tag
    delete = None

    # check it no longer appears
    delete = make_request('list remove %s %s' % (tag, existsid))
    assert delete['state'] == 2
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag)
    assert empty2['state'] == 2
    empty2 = None


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
        assert newitem['state'] == 1
        newitem = None

    # check four items exist
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 4

    # check they are in the same order we added them
    e = 0
    for i in range(0, 4):
        assert exists['data'][e][0] == '%s%d' % (listitem, i)
        e += 1

    exists = None

    list_empty(tag)


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
    assert newitem['state'] == 1
    newitem = None

    exists = make_request('list view %s' % tagalt)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    altitemid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # add two new items to correct tag
    for i in range(0, 2):
        newitem = make_request('list add %s %s' % (tag, '%s%d' % (listitem, i)))
        assert newitem['state'] == 1
        newitem = None

    # check two items exist
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
    assert len(exists['data']) == 2
    exists = None

    # add tag to alternate item, adding it to the *end* of this list
    newitem = make_request('list tag %s %s' % (altitemid, tag))
    assert newitem['state'] == 1
    newitem = None

    # check three items exist
    exists = make_request('list view %s' % tag)
    assert exists['state'] == 1
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


def list_missingtag_test():
    '''
    Test handling of empty tags
    '''
    newitem = make_request('list add  item')
    assert newitem['state'] == 2
    assert newitem['message'] == 'No tag specified'
    newitem = None

    newitem = make_request('list tag 1 ')
    assert newitem['state'] == 2
    assert newitem['message'] == 'No tag specified'
    newitem = None


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
    assert newitem['state'] == 1
    newitem = None

    # check new item exists
    exists = make_request('list view %s' % tag_origin)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    existsid = exists['data'][0][2]['Delete'].split(' ')[3]
    exists = None

    # fail to move item from wrong tag
    wrongtag = make_request('list move %s %s %s' % (existsid, 'UNITESTNONEXISTANTTAG', tag_dest))
    assert wrongtag['state'] == 2
    wrongtag = None

    # move item to new tag
    newtag = make_request('list move %s %s %s' % (existsid, tag_origin, tag_dest))
    assert newtag['state'] == 1
    newtag = None

    # check item only shows once
    exists = make_request('list view %s' % tag_dest)
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None

    # check it no longer appears at old tag
    old = make_request('list view %s' % (tag_origin))
    assert old['state'] == 2
    old = None

    # delete list item
    delete = make_request('list remove %s %s' % (tag_dest, existsid))
    assert delete['state'] == 1
    assert len(delete['data']) == 1
    assert delete['data'][0][0] == 'View list "%s"' % tag_dest
    delete = None

    # check list is empty again
    empty2 = make_request('list view %s' % tag_origin)
    assert empty2['state'] == 2
    empty2 = None

    # check list is empty again
    empty3 = make_request('list view %s' % tag_dest)
    assert empty3['state'] == 2
    empty3 = None


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
    assert newitem['state'] == 1
    itemid = newitem['data'][0][2]['Delete'].split(' ')[3]
    newitem = None

    # add new item with first tag
    newitem = make_request('list add %s %s' % (tag_one, listitemsingle))
    assert newitem['state'] == 1
    newitem = None

    # add new item with second tag
    newitem = make_request('list add %s %s' % (tag_two, listitemsingle))
    assert newitem['state'] == 1
    newitem = None

    # add second tag to first item
    newitem = make_request('list tag %s %s' % (itemid, tag_two))
    assert newitem['state'] == 1
    newitem = None

    # check two items in first tag
    exists = make_request('list view %s' % tag_one)
    assert exists['state'] == 1
    assert len(exists['data']) == 2
    exists = None

    # check one item in second tag
    exists = make_request('list view %s' % tag_two)
    assert exists['state'] == 1
    assert len(exists['data']) == 2
    exists = None

    # check one item when loading both tags!
    exists = make_request('list view %s %s' % (tag_one, tag_two))
    assert exists['state'] == 1
    assert len(exists['data']) == 1
    assert exists['data'][0][0] == listitem
    exists = None
