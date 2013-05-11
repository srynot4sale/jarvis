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
    assert len(negative['data']) == 0

def weather_test():
    '''
    Test home page shows weather
    '''
    weather = make_request('server connect')
    assert weather['data'][0][0].startswith('Today')
    assert weather['data'][1][0].startswith('Tomorrow')

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
        'UNITTESTLISTBAD%20',
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
    newtag = make_request('list tag %s %s' % (tag2, existsid))
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
    newtag = make_request('list tag %s %s' % (tag, existsid))
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
