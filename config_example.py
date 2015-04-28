#
# THIS AN EXAMPLE CONFIG FILE
#

config = {}

# THIS OPTION VERY IMPORTANT!
# Set to True on production sites, prevent tests running
# and potentially wiping all your data
config['is_production']         = True

# Name that Jarvis will refer to you by
config['username']              = 'My Name'

# Your email address
config['email']                 = 'you@example.com'

# Optional, when set to True displays debugging data
#config['debug']                 = False

# Database configuration. DB username is used as dbname
config['database_host']         = 'localhost'
config['database_username']     = 'jarvis'
config['database_password']     = 'password'

# Port to run server on
config['interface_http_port']   = 'XXXX'

# Passphrase for signing cookies
config['secret']                = 'secrethash'

# Timezone you'd prefer times displayed as in clients
config['timezone']              = 'Pacific/Auckland'

# URL the web client is accessible at. Normally would be
# those hostname/ip of server and the port defined earlier.
# However, could be different if you are running the server
# behind a proxy, e.g. apache for HTTPS
config['web_baseurl']           = 'http://localhost:XXXX/'

# Set the username/password for using the web client
config['web_username']          = 'myusername'
config['web_password']          = 'mypassword'

# Jarvis from address
config['email_from_address']    = 'jarvis@example.com'
config['email_from_name']       = 'Jarvis'
