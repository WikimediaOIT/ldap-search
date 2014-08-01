#!/usr/bin/python

"""
Simple script to walk LDAP and provide CSV output of user emails
"""

import ldap
import argparse
import sys
import os

# Enable debugging for more output
DEBUG=False

# Parse command line options
parser = argparse.ArgumentParser(description="Simple LDAP User Dump")
parser.add_argument('-s', '--server',  help='LDAP Server')
parser.add_argument('-b', '--base',    help='LDAP Search base')
args = parser.parse_args()

# Make sure we have needed variables
# If command line option was not given, check for environment variable, otherwise fail
if args.server is None and os.environ.get('LDAP_SERVER'):
    args.server = os.environ.get('LDAP_SERVER')
elif args.server is None:
    print 'ERROR: LDAP Server not given'
    parser.print_help()
    sys.exit(2)

if args.base is None and os.environ.get('LDAP_BASE'):
    args.base = os.environ.get('LDAP_BASE')
    # eg. "ou=people,dc=corp,dc=wikimedia,dc=org"
elif args.base is None:
    print 'ERROR: LDAP Search base not given'
    parser.print_help()
    sys.exit(2)

# Debugging inputs
if DEBUG:
    print 'DEBUG Server:      ', args.server
    print 'DEBUG Search Base: ', args.base

# Ignore certificate errors (self signed cert)
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

# Connect and go secure
con = ldap.initialize('ldap://%s' % (args.server))
con.start_tls_s()

# Search settings
searchScope        = ldap.SCOPE_SUBTREE
searchFilter       = "cn=*"

# Try your search parameters
try:
    ldap_result_id = con.search(args.base, 
            searchScope, 
            searchFilter)
    result_set = []
    while 1:
        result_type, result_data = con.result(ldap_result_id, 0)
        if (result_data == []):
            break
        else:
            # append results to a list
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)
except ldap.LDAPError, e:
    print e

# Walk all records and display fields we care about in csv
for record in result_set:
    # Skip bogus records that don't have the fields we care about
    if 'sn' not in record[0][1]: continue
    if 'givenName' not in record[0][1]: continue
    if 'mail' not in record[0][1]: continue

    # Print out
    print '%s,%s,%s' % (
        record[0][1]['givenName'][0],
        record[0][1]['sn'][0],
        record[0][1]['mail'][0],
        )
