import test
import functions.function


class list_testcase(test.jarvis_testcase):

    # Utility functions
    # Reset a list by deleting all items
    def list_empty(self, tag):
        exist = self.http_request('list view %s' % tag)
        if exist['message'] != 'List "%s" contents' % tag:
            return

        for item in exist['data']:
            self.http_request(item[2]['Delete'])


    def list_add_weirdtag_test(self):
        '''
        Test adding a list item with weird characters in tag

        !Tests: list_add
        !Tests: list_view
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
            newitem = self.http_request('list add %s %s' % (b, good))
            assert newitem['state'] == functions.function.STATE_SUCCESS
            newitem = None

            # check new item exists
            exists = self.http_request('list view %s' % b)
            assert exists['state'] == functions.function.STATE_SUCCESS
            assert len(exists['data']) == 1
            if exists['data'][0][0] != good:
                raise Exception(b)
            assert exists['data'][0][0] == good
            exists_delete = exists['data'][0][2]['Delete']
            exists = None

            # delete list item
            delete = self.http_request(exists_delete)
            assert delete['state'] == functions.function.STATE_SUCCESS
            delete = None

            # check list is empty again
            empty2 = self.http_request('list view %s' % b)
            assert len(empty2['data']) == 0
            empty2 = None

            self.list_empty(b)


    def list_adddeleteitem_test(self):
        '''
        Test adding and deleting list items

        !Tests: list_add
        !Tests: list_delete
        '''
        tag = 'UNITTESTLIST'
        listitem = 'test list item'

        # add new item
        newitem = self.http_request('list add %s %s' % (tag, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        assert newitem['write'] == True
        newitem = None

        # check new item exists
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        exists_delete = exists['data'][0][2]['Delete']
        exists = None

        # delete list item
        delete = self.http_request(exists_delete)
        assert delete['state'] == functions.function.STATE_SUCCESS
        delete = None

        # check list is empty again
        empty2 = self.http_request('list view %s' % tag)
        assert len(empty2['data']) == 0
        empty2 = None


    def list_adddeletetags_test(self):
        '''
        Test adding and removing tags from list items

        !Tests: list_add
        !Tests: list_tag
        !Tests: list_delete
        '''
        tag = 'UNITTESTTAG1'
        tag2 = 'UNITTESTTAG2'
        listitem = 'test list tag item'

        # add new item with first tag
        newitem = self.http_request('list add %s %s' % (tag, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # check new item exists
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        existsid = exists['data'][0][2]['Delete'].split(' ')[3]
        exists = None

        # add second tag
        newtag = self.http_request('list tag %s %s' % (existsid, tag2))
        assert newtag['state'] == functions.function.STATE_SUCCESS
        newtag = None

        # check new item exists
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        exists = self.http_request('list view %s' % tag2)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        exists = None

        # delete list item
        delete = self.http_request('list delete %s %s' % (tag, existsid))
        assert delete['state'] == functions.function.STATE_SUCCESS
        delete = None

        # already deleted
        delete = self.http_request('list delete %s %s' % (tag, existsid))
        assert delete['state'] == functions.function.STATE_FAILURE
        delete = None

        delete = self.http_request('list delete %s %s' % (tag2, existsid))
        assert delete['state'] == functions.function.STATE_SUCCESS
        assert 'redirected' in delete
        delete = None

        # check list is empty again
        empty2 = self.http_request('list view %s' % tag)
        assert len(empty2['data']) == 0
        empty2 = self.http_request('list view %s' % tag2)
        assert len(empty2['data']) == 0
        empty2 = None


    def list_addmultipletags_test(self):
        '''
        Check adding the same tag twice to a list item doesn't make
        it appear twice, or need to be deleted twice

        !Tests: list_add
        !Tests: list_tag
        !Tests: list_view
        !Tests: list_delete
        '''
        tag = 'UNITTESTTAGSDOUBLEUP'
        listitem = 'test list tag item'

        # add new item with first tag
        newitem = self.http_request('list add %s %s' % (tag, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # check new item exists
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        existsid = exists['data'][0][2]['Delete'].split(' ')[3]
        exists = None

        # add same tag again
        newtag = self.http_request('list tag %s %s' % (existsid, tag))
        assert newtag['state'] == functions.function.STATE_SUCCESS
        newtag = None

        # check item only shows once
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        exists = None

        # delete list item
        delete = self.http_request('list delete %s %s' % (tag, existsid))
        assert delete['state'] == functions.function.STATE_SUCCESS
        assert 'redirected' in delete
        delete = None

        # check it no longer appears
        delete = self.http_request('list delete %s %s' % (tag, existsid))
        assert delete['state'] == functions.function.STATE_FAILURE
        delete = None

        # check list is empty again
        empty2 = self.http_request('list view %s' % tag)
        assert len(empty2['data']) == 0
        empty2 = None


    def list_itemorder_basic_test(self):
        '''
        Check items appear in order added when displayed

        !Tests: list_view
        '''
        tag = 'UNITTESTLISTORDER'
        listitem = 'test list item item#'

        # add four new items
        for i in range(0, 4):
            newitem = self.http_request('list add %s %s' % (tag, '%s%d' % (listitem, i)))
            assert newitem['state'] == functions.function.STATE_SUCCESS
            newitem = None

        # check four items exist
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 4

        # check they are in the same order we added them
        e = 0
        for i in range(0, 4):
            assert exists['data'][e][0] == '%s%d' % (listitem, i)
            e += 1

        exists = None


    def list_itemorder_multitag_test(self):
        '''
        Check items appear in order tag's were added when displayed

        !Tests: list_tag
        !Tests: list_view
        '''
        tag = 'UNITTESTLISTORDERTAG'
        tagalt = 'UNITTESTLISTORDERTAGALT'
        listitem = 'test list item item#'

        # check for empty lists first
        self.list_empty(tag)
        self.list_empty(tagalt)

        # add item to alternate list first
        newitem = self.http_request('list add %s %s' % (tagalt, '%s%d' % (listitem, 9)))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        exists = self.http_request('list view %s' % tagalt)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        altitemid = exists['data'][0][2]['Delete'].split(' ')[3]
        exists = None

        # add two new items to correct tag
        for i in range(0, 2):
            newitem = self.http_request('list add %s %s' % (tag, '%s%d' % (listitem, i)))
            assert newitem['state'] == functions.function.STATE_SUCCESS
            newitem = None

        # check two items exist
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 2
        exists = None

        # add tag to alternate item, adding it to the *end* of this list
        newitem = self.http_request('list tag %s %s' % (altitemid, tag))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # check three items exist
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 3

        # check they are in the same order we added the tags
        # this means that the alternate item should be last on the list
        expect = [0, 1, 9]
        e = 0
        for i in expect:
            assert exists['data'][e][0] == '%s%d' % (listitem, i)
            e += 1

        exists = None


    def list_missingtag_test(self):
        '''
        Test handling of empty tags

        !Tests: list_add
        !Tests: list_tag
        '''
        newitem = self.http_request('list add  item')
        assert newitem['state'] == functions.function.STATE_FAILURE
        assert newitem['message'] == 'No tag specified'
        newitem = None

        newitem = self.http_request('list tag 1 ')
        assert newitem['state'] == functions.function.STATE_FAILURE
        assert newitem['message'] == 'No tag specified'
        newitem = None


    def list_move_test(self):
        '''
        Test the list move action

        !Tests: list_move
        '''
        tag_origin = 'UNITTESTORIGIN'
        tag_dest = 'UNITTESTDESTINATION'
        listitem = 'tagitem'

        # check for empty lists first
        self.list_empty(tag_origin)
        self.list_empty(tag_dest)

        # add new item with first tag
        newitem = self.http_request('list add %s %s' % (tag_origin, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # check new item exists
        exists = self.http_request('list view %s' % tag_origin)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        existsid = exists['data'][0][2]['Delete'].split(' ')[3]
        exists = None

        # fail to move item from wrong tag
        wrongtag = self.http_request('list move %s %s %s' % (existsid, 'UNITESTNONEXISTANTTAG', tag_dest))
        assert wrongtag['state'] == functions.function.STATE_FAILURE
        wrongtag = None

        # move item to new tag
        newtag = self.http_request('list move %s %s %s' % (existsid, tag_origin, tag_dest))
        assert newtag['state'] == functions.function.STATE_SUCCESS
        newtag = None

        # check item only shows once
        exists = self.http_request('list view %s' % tag_dest)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        exists = None

        # check it no longer appears at old tag
        old = self.http_request('list view %s' % (tag_origin))
        assert len(old['data']) == 0
        old = None

        # delete list item
        delete = self.http_request('list delete %s %s' % (tag_dest, existsid))
        assert delete['state'] == functions.function.STATE_SUCCESS
        assert 'redirected' in delete
        delete = None

        # check list is empty again
        empty2 = self.http_request('list view %s' % tag_origin)
        assert len(empty2['data']) == 0
        empty2 = None

        # check list is empty again
        empty3 = self.http_request('list view %s' % tag_dest)
        assert len(empty3['data']) == 0
        empty3 = None


    def list_multipletagview_test(self):
        '''
        Test the list view with multiple tags

        !Tests: list_view
        '''
        tag_one = 'UNITTESTTAG1'
        tag_two = 'UNITTESTTAG2'
        listitem = 'tagitemtwotags'
        listitemsingle = 'tagitemonetag'

        # check for empty lists first
        self.list_empty(tag_one)
        self.list_empty(tag_two)

        # add new item with first tag
        newitem = self.http_request('list add %s %s' % (tag_one, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        itemid = newitem['data'][0][2]['Delete'].split(' ')[3]
        newitem = None

        # add new item with first tag
        newitem = self.http_request('list add %s %s' % (tag_one, listitemsingle))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # add new item with second tag
        newitem = self.http_request('list add %s %s' % (tag_two, listitemsingle))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # add second tag to first item
        newitem = self.http_request('list tag %s %s' % (itemid, tag_two))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # check two items in first tag
        exists = self.http_request('list view %s' % tag_one)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 2
        exists = None

        # check one item in second tag
        exists = self.http_request('list view %s' % tag_two)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 2
        exists = None

        # check one item when loading both tags!
        exists = self.http_request('list view %s %s' % (tag_one, tag_two))
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        exists = None


    def list_addmoveitem_test(self):
        '''
        Test adding and moving list items

        !Tests: list_add
        !Tests: list_move
        '''
        tag1 = 'TestTag1'
        tag2 = 'TestTag2'
        listitem = 'test list item'

        # Add new item
        newitem = self.http_request('list add %s %s' % (tag1, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        assert newitem['write'] == True
        newitem = None

        # check new item exists
        exists = self.http_request('list view %s' % tag1)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        itemid = exists['data'][0][3]['id']
        exists = None

        # Move new item
        move = self.http_request('list move %s %s %s' % (itemid, tag1, tag2))
        assert move['state'] == functions.function.STATE_SUCCESS
        assert len(move['data']) == 1
        assert move['data'][0][0] == listitem

        # Check to see if tag1 list is empty
        empty = self.http_request('list view %s' % tag1)
        assert empty['state'] == functions.function.STATE_SUCCESS
        assert len(empty['data']) == 0

        # Make sure item is in list 2
        moved = self.http_request('list view %s' % tag2)
        assert moved['state'] == functions.function.STATE_SUCCESS
        assert len(moved['data']) == 1
        assert moved['data'][0][0] == listitem


    def list_list_test(self):
        '''
        Test list list function to make sure correct result is given

        !Tests: list_add
        !Tests: list_list
        '''

        tag1 = 'testtag1'
        tag2 = 'testtag2'
        systemtag = '!testing'

        listitem = 'test list item'

        # Add new item
        newitem = self.http_request('list add %s %s' % (tag1, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Check length of list
        testlist = self.http_request('list list')
        assert testlist['state'] == functions.function.STATE_SUCCESS
        assert len(testlist['data']) == 1
        testlist = None

        # Add system list item
        newitem = self.http_request('list add %s %s' % (systemtag, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Check that system item isn't included in list_list
        testlist = self.http_request('list list')
        assert testlist['state'] == functions.function.STATE_SUCCESS
        assert len(testlist['data']) == 1
        testlist = None

        # Add new item
        newitem = self.http_request('list add %s %s' % (tag2, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Check length of list
        testlist = self.http_request('list list')
        assert testlist['state'] == functions.function.STATE_SUCCESS
        assert len(testlist['data']) == 2
        testlist = None


    def list_default_test(self):
        '''
        Test the default list action returns successfully

        !Tests: list_default
        '''
        default = self.http_request('list default')
        assert default['state'] == functions.function.STATE_SUCCESS


    def list_update_test(self):
        '''
        Test updating of a list item

        !Tests: list_update
        !Tests: list_add
        !Tests: list_view
        '''

        tag = 'testlist'
        listitem = 'test list item'
        listitemupdate = 'updated list item'

        # Add new item
        newitem = self.http_request('list add %s %s' % (tag, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Make sure item exist with the correct name
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem
        itemid = exists['data'][0][3]['id']
        exist = None

        # Update item
        update = self.http_request('list update %s %s %s' % (tag, itemid, listitemupdate))
        assert update['state'] == functions.function.STATE_SUCCESS
        assert update['write'] == True

        # Check item has been updated
        check = self.http_request('list view %s' % tag)
        assert check['state'] == functions.function.STATE_SUCCESS
        assert len(check['data']) == 1
        assert check['data'][0][0] == listitemupdate
        check = None


    def list_update_missing_test(self):
        '''
        Update non-existant list item

        !Tests: list_update
        '''
        tag = 'notreal'
        itemid = 3444455
        listitemupdate = 'This item doesn\'t exist'

        # Update item
        update = self.http_request('list update %s %s %s' % (tag, itemid, listitemupdate))
        assert update['state'] == functions.function.STATE_FAILURE
        assert update['write'] == True
        assert len(update['data']) == 1


    def list_update_unchanged_test(self):
        '''
        Test a new version isn't created if the updated text hasn't changed

        !Tests: list_update
        !Tests: list_add
        !Tests: list_view
        !Tests: list_history
        '''

        tag = 'testlist'
        listitem = 'test list item'

        # Add new item
        newitem = self.http_request('list add %s %s' % (tag, listitem))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Make sure item exist with the correct name
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        itemid = exists['data'][0][3]['id']
        exist = None

        # Update item with same text
        update = self.http_request('list update %s %s %s' % (tag, itemid, listitem))
        assert update['state'] == functions.function.STATE_FAILURE
        assert update['write'] == True

        # Check item has no history
        check = self.http_request('list history %s' % itemid)
        assert check['state'] == functions.function.STATE_SUCCESS
        assert len(check['data']) == 0
        check = None


    def list_update_order_test(self):
        '''
        Test order of list doesn't change when updating a list item

        !Tests: list_update
        !Tests: list_add
        !Tests: list_view
        '''

        tag = 'testlist'
        listitem = 'test list item'
        listitemupdate = 'updated list item'

        # Add 3 new items
        for i in range(1, 4):
            newitem = self.http_request('list add %s %s%d' % (tag, listitem, i))
            assert newitem['state'] == functions.function.STATE_SUCCESS
            newitem = None

        # Make sure item exist with the correct name
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 3
        assert exists['data'][1][0] == '%s%d' % (listitem, 2)
        itemid = exists['data'][1][3]['id']
        exist = None

        # Update item
        update = self.http_request('list update %s %s %s' % (tag, itemid, listitemupdate))
        assert update['state'] == functions.function.STATE_SUCCESS
        assert update['write'] == True

        # Check item has been updated and remains in same place
        check = self.http_request('list view %s' % tag)
        assert check['state'] == functions.function.STATE_SUCCESS
        assert len(check['data']) == 3
        assert check['data'][1][0] == listitemupdate
        check = None


    def list_update_version_test(self):
        '''
        Test list item versions saved when updating

        !Tests: list_update
        !Tests: list_add
        !Tests: list_view
        !Tests: list_history
        '''

        tag = 'testlist'
        listitems = [
            'test list item original',
            'test list item first edit',
            'test list item second edit',
            'test list item third edit',
            'test list item final',
        ]

        # Add new item
        item = self.http_request('list add %s %s' % (tag, listitems[0]))
        assert item['state'] == functions.function.STATE_SUCCESS
        item = None

        # Make sure item exists
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        itemid = exists['data'][0][3]['id']
        exist = None

        # Update item a few times
        for listitem in listitems[1:]:
            item = self.http_request('list update %s %s %s' % (tag, itemid, listitem))
            assert item['state'] == functions.function.STATE_SUCCESS
            item = None

        # Make sure item exists with the latest name
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitems[4]
        exist = None

        # Check for item update history
        check = self.http_request('list history %s' % itemid)
        assert check['state'] == functions.function.STATE_SUCCESS
        assert len(check['data']) == 4

        i = 3
        for listitem in listitems[0:-1]:
            assert check['data'][i][0] == listitem
            i -= 1

        check = None


    def list_unicode_test(self):
        '''
        Test adding of items that include unicode characters

        !Tests: list_add
        '''

        tag = 'testlist'
        listitem1 = 'test \xc2 100'
        listitem2 = 'This is a \xe2 test \xe2'

        # Add first item
        newitem = self.http_request('list add %s %s' % (tag, listitem1))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Make sure item exist with the correct name
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem1
        exist = None

        # Add first item
        newitem = self.http_request('list add %s %s' % (tag, listitem2))
        assert newitem['state'] == functions.function.STATE_SUCCESS
        newitem = None

        # Make sure item exist with the correct name
        exists = self.http_request('list view %s' % tag)
        assert exists['state'] == functions.function.STATE_SUCCESS
        assert len(exists['data']) == 1
        assert exists['data'][0][0] == listitem2
        exist = None


    def list_normalise_tags_test(self):
        return
        assert functions.list.normalise_tag('tag') == 'tag'
        assert functions.list.normalise_tag('Tag') == 'tag'
        assert functions.list.normalise_tag('#tag') == 'tag'
        assert functions.list.normalise_tag(' tag ') == 'tag'
        assert functions.list.normalise_tag('ta-g') == 'tag'
        assert functions.list.normalise_tag('tag3') == 'tag3'
        assert functions.list.normalise_tag('TAG4') == 'tag4'
        assert functions.list.normalise_tag('t a g t a g') == 'tagtag'
        assert functions.list.normalise_tag('!tag') == '!tag'
