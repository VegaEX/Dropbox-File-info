
import urllib
import urllib2
import json
import argparse
import sys
import csv
from collections import Counter

reload(sys)
sys.setdefaultencoding('UTF8')

parser = argparse.ArgumentParser(description='Lists all files by user in the Dropbox for Business  Team.')
parser.add_argument('-e','--excluded_users',dest='excluded_users',action='append',help='Pass a filename which contains a list of email addresses of users to exclude.')
parser.add_argument('-u', '--user', dest='users', action='append', help='Target user (email address) to scan.  All team members will be returned if unspecified. You may pass multiple -u arguments.')
parser.add_argument('-b', '--batch_process_users', dest='batch_users', action='append', help='Pass a filename which contains users to batch process.')

args = parser.parse_args()

dfbToken = raw_input('Enter your Dropbox Business API App token (Team Member File Access permission): ')

#Pull member from an email address
def getDfbMember(email):
    request = urllib2.Request('https://api.dropbox.com/1/team/members/get_info', json.dumps({'email':email}))
    request.add_header("Authorization", "Bearer "+dfbToken)
    request.add_header("Content-type", 'application/json')
    try:

        response = json.loads(urllib2.urlopen(request).read())
        print(response["profile"]["email"])

        if(response["profile"]["email"] not in excluded_users):
            return json.loads(urllib2.urlopen(request).read())
        else:
            print('Excluded user : %s' % email)
            return None

    # Exit on error here with response.
    except urllib2.HTTPError, error:
        parser.error(error.read());

# Get all members.
def getDfbMembers(cursor):
    data = {"limit":100}

    if cursor is not None:
        data["cursor"] = cursor

    request = urllib2.Request('https://api.dropbox.com/1/team/members/list', json.dumps(data))
    request.add_header("Authorization", "Bearer "+dfbToken)
    request.add_header("Content-type", 'application/json')
    try:
        response = json.loads(urllib2.urlopen(request).read())
        members = response["members"]

        if response["has_more"]:
            members = members + getDfbMembers(cursor=response["cursor"])

        #  filter the members against exclusions
        for index, member in enumerate(members):

            print('MEMBER IN EXCLUDED USERS? : %s',member in excluded_users)
            if(member in excluded_users):
                _deletedMember = members.pop(index)
                print('Excluded User: %s',_deletedMember)

        return members

    except urllib2.HTTPError, error:
        parser.error(error.read())

# List user's dropbox
def listFiles(memberEmail, memberId, csvwriter):
    cursor = None
    num_files = 0

    try:
        while True:
            params = {}
            if cursor is not None:
                params['cursor'] = cursor
            request = urllib2.Request('https://api.dropboxapi.com/1/delta', data=urllib.urlencode(params))
            request.add_header("Authorization", "Bearer "+dfbToken)
            request.add_header("X-Dropbox-Perform-As-Team-Member", memberId)

            response_string = urllib2.urlopen(request).read()
            response = json.loads(response_string)

            ZSTools ="ZS Tools & Utilities (1)"
            ZSTools2 = "ZS Tools & Utilities"
            NewHireOnBoarding = "New Hire On-Boarding Reading (1)"
            NewHireForms = "New Hire Forms & Information (1)"
            SOPLink = "SOP Link (1)"
            DocumentsForReview = "Documents for Review (1)"
            DocumentsForReview2 = "Documents for Review"
            GetStartedDropbox = "Get Started with Dropbox"
            MarketAccess = "/Market Access/"

            for path, md in response["entries"]:
                if md is None:
                    pass  # Delete entry.  Skip it.
                else:

                    shared = False
                    if 'parent_shared_folder_id' in md or 'shared_folder' in md:
                        shared = True

                    if ZSTools.lower() not in md['path'].lower() and ZSTools2.lower() not in md['path'].lower() and NewHireOnBoarding.lower() not in md['path'].lower() \
                            and SOPLink.lower() not in md['path'].lower() and DocumentsForReview.lower() not in md['path'].lower() and DocumentsForReview2.lower() not in md['path'].lower() \
                            and NewHireForms.lower() not in md['path'].lower() and GetStartedDropbox.lower() not in md['path'].lower()\
                            and MarketAccess.lower() not in md['path'].lower():

                        if md["is_dir"]:
                            csvwriter.writerow([memberEmail, md["path"].encode("utf-8"), "Folder", "-", "-", md["modified"], str(shared)])
                        else:
                            csvwriter.writerow([memberEmail, md["path"].encode("utf-8"), md["mime_type"], str(md["bytes"]), md["size"], md["modified"], str(shared)])
                        num_files += 1

            if response["reset"] and cursor is not None:
                sys.stderr.write("  ERROR: got a reset!")
                csvwriter.writerow([memberEmail, "/delta with cursor={!r} returned RESET".format(cursor), "ERROR", "-", "-", "-", "-"])
                break

            cursor = response['cursor']

            if not response['has_more']:
                break

        sys.stderr.write("  Finished listing {} files/folders for {} \n".format(num_files, memberEmail))


    except urllib2.HTTPError as error:
        csvwriter.writerow([memberEmail, "/delta with cursor={!r} unknown error".format(cursor), "ERROR", "-", "-", "-", "-", "-"])
        sys.stderr.write("  ERROR: {}\n".format(error))


def formatSize(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

# check users.
members = []
excluded_users = []
batch_users = []

if(args.excluded_users is not None):
    excluded_users = args.excluded_users
    excludedUsersFile = open('excludedusers.csv',"r")
    excluded_users = excludedUsersFile.read().split()
    print(excluded_users)

#print('user@domain.com' in excluded_users)
if(args.batch_users is not None):
    batch_users = args.batch_users
    batch_users_file = open('batch_users.csv','rw')
    batch_users = batch_users_file.read().split()

    members = map(getDfbMember,batch_users)

if (args.users is not None):
    members = map(getDfbMember, args.users)

ofile  = open('ZSPharmaTeamMemberFiles.csv', "wb")
csvwriter = csv.writer(ofile, dialect='excel', quotechar='"', quoting=csv.QUOTE_ALL)
csvwriter.writerow(['User', 'Path', 'Type', 'Size (bytes)', 'Size (formatted)', 'Modified', 'Shared'])

sorted_members = sorted(members)

for member in sorted_members:
    if(member is not None):
        if member["profile"]["status"] == "active":
            #print(member["profile"]["email"])
            files = listFiles(member["profile"]["email"], member["profile"]["member_id"], csvwriter)
