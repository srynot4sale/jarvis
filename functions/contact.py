import data.model
import function
import kernel.action


class controller(function.function):
    def list(self):
        datasource = self.get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_contact_entities
            WHERE
                deleted IS NULL
            ORDER BY
                `name` ASC
        """
        results = datasource.get_records(sql)
        entities = []
        for r in results:
            entities.append(Contact(self, r))
        return entities

    def get_accounts(self, c):
        datasource = self.get_data_source()
        sql = """
            SELECT
                *
            FROM
                function_contact_accounts
            WHERE
                deleted IS NULL
            AND contact_id = %s
            ORDER BY
                `type` ASC,
                `uid` ASC
        """
        data = [c.id]
        results = datasource.get_records(sql, data)
        accounts = []
        for r in results:
            accounts.append(Account(self, r))
        return accounts


class Contact(data.model.model):
    """
    Contact model
    """
    _params = ('id', 'name', 'added', 'deleted')

    def _create_sql(self):
        sql = """
            INSERT INTO
                function_contact_entities
                (name, added, deleted)
            VALUES
                (%s, NOW(), NULL)
        """
        data = [self.name]
        return (sql, data)

    def _load_sql(self):
        sql = """
            SELECT
                *
            FROM
                function_contact_entities
            WHERE
                id = %s
            AND deleted IS NULL
        """
        data = [self.id]
        return (sql, data)

    def _delete_sql(self):
        sql = """
            UPDATE
                function_contact_entities
             SET deleted = NOW()
            WHERE
                id = %s
        """
        data = [self.id]
        return (sql, data)

    def _update_sql(self):
        sql = """
            UPDATE
                function_contact_entities
             SET name = %s
            WHERE
                id = %s
        """
        data = [self.name, self.id]
        return (sql, data)

    def get_accounts(self):
        return self._function.get_accounts(self)


class Account(data.model.model):
    """
    Contact account model
    """
    _params = ('id', 'contact_id', 'type', 'uid', 'added', 'deleted')

    def _set_type(self, type):
        return type.lower()

    def _create_sql(self):
        sql = """
            INSERT INTO
                function_contact_accounts
                (contact_id, type, uid, added, deleted)
            VALUES
                (%s, %s, %s, NOW(), NULL)
        """
        data = [self.contact_id, self.type, self.uid]
        return (sql, data)

    def _load_sql(self):
        sql = """
            SELECT
                *
            FROM
                function_contact_accounts
            WHERE
                deleted IS NULL
            AND id = %s
        """
        data = [self.id]
        return (sql, data)

    def _delete_sql(self):
        sql = """
            UPDATE
                function_contact_accounts
             SET deleted = NOW()
            WHERE
                id = %s
        """
        data = [self.id]
        return (sql, data)


class action_list(kernel.action.action):
    """
    List all contacts
    """
    def execute(self, data):
        contacts = self.function.list()
        data = []
        for c in contacts:
            data.append([c.name, 'contact view %s' % c.id])

        actions = [('Add new...', 'contact add %Full_name')]

        return function.response(function.STATE_SUCCESS, 'Contacts list', data, actions)


class action_add(kernel.action.action):
    """
    Add a new contact
    """
    usage = '$name'

    def execute(self, data):

        name = ' '.join(data).strip()

        if name == '':
            return function.response(function.STATE_FAILURE, 'No name supplied')

        c = Contact(self.function, {'name': name})
        c.create()

        return function.redirect(self, ('contact', 'list'), 'Added contact "%s"' % c.name)


class action_view(kernel.action.action):
    """
    View contact
    """
    usage = '$contactid'

    def execute(self, data):
        contactid = data[0]

        c = self.function.get_model_instance(Contact, contactid)
        if not c:
            return function.response(function.STATE_FAILURE, 'Contact with id "%s" cannot be found' % contactid)

        accounts = c.get_accounts()
        data = []
        for a in accounts:
            data.append([
                '%s: %s' % (a.type, a.uid),
                None,
                {
                    'Delete': 'contact accountdelete %s %s' % (a.contact_id, a.id) 
                }
            ])

        actions = [
            ('Add new account...', 'contact accountadd %s %%Type %%UID' % (contactid)),
            ('Delete', 'contact delete %s' % (contactid)),
            ('Edit...', 'contact edit %s %%Name{{%s}}' % (contactid, c.name)),
            ('Contact list', 'contact list')
        ]

        return function.response(function.STATE_SUCCESS, c.name, data, actions)


class action_edit(kernel.action.action):
    """
    Edit a contact
    """
    usage = '$contactid'

    def execute(self, data):
        contactid = data[0]
        name = ' '.join(data[1:]).strip()

        c = self.function.get_model_instance(Contact, contactid)
        if not c:
            return function.response(function.STATE_FAILURE, 'Contact with id "%s" cannot be found' % contactid)

        oldname = c.name
        c.name = name
        c.update()

        return function.redirect(
                self,
                ('contact', 'view', contactid),
                'Contact "%s" updated to "%s"' % (oldname, c.name)
        )


class action_delete(kernel.action.action):
    """
    Delete a contact
    """
    usage = '$contactid'

    def execute(self, data):
        contactid = data[0]

        c = self.function.get_model_instance(Contact, contactid)
        if not c:
            return function.response(function.STATE_FAILURE, 'Contact with id "%s" cannot be found' % contactid)

        c.delete()

        return function.redirect(
                self,
                ('contact', 'list'),
                'Deleted contact "%s"' % (c.name)
        )


class action_accountadd(kernel.action.action):
    """
    Add a new account to a contact
    """
    usage = '$contactid $accounttype $accountuid'

    def execute(self, data):
        contactid = data[0]
        acctype = data[1]
        uid = data[2]

        c = self.function.get_model_instance(Contact, contactid)
        if not c:
            return function.response(function.STATE_FAILURE, 'Contact with id "%s" cannot be found' % contactid)

        a = Account(
            self.function,
            {
                'contact_id': contactid,
                'type': acctype,
                'uid': uid
            }
        )
        a.create()

        return function.redirect(
                self,
                ('contact', 'view', contactid),
                'Added "%s" account to contact "%s"' % (acctype, c.name)
        )


class action_accountdelete(kernel.action.action):
    """
    Delete an account from a contact
    """
    usage = '$contactid $accountid'

    def execute(self, data):
        contactid = data[0]
        accountid = data[1]

        c = self.function.get_model_instance(Contact, contactid)
        if not c:
            return function.response(function.STATE_FAILURE, 'Contact with id "%s" cannot be found' % contactid)

        a = self.function.get_model_instance(Account, accountid)
        if not a:
            return function.response(function.STATE_FAILURE, 'Contact with id "%s" cannot be found' % contactid)

        a.delete()

        return function.redirect(
                self,
                ('contact', 'view', contactid),
                'Deleted "%s" account from contact "%s"' % (a.type, c.name)
        )
