Purpose Summary

This script was created in an effort to better streamline a large-scale Dropbox to Google file migration. There was a push to downsize, and eventually remove entirely, the companies Business grade Dropbox Teams account.We needed to be able to quickly gather data from the Dropbox account to better determine which teams/departments had the largest storage usage so we could take this information back to department heads. It was then up to the department heads to come up with a business justification to remain active in Dropbox, otherwise the department's files were scheduled for cloning over into Gsuite.




Script Breakdown

To start the script with request input of an API token for the specific team being exported. This can be generated by a Dropbox Super Admin account. Additionally a non-team specific API token can be generated and it will pull information from all users on the account, however this takes additional time depending on the storage usage of each team.
All user emails in the specified team are pulled with a ‘get_info” API call.
For each of these users it will cross reference their email against an excluded user list if that argument was passed.
For the users not excluded in the list the script will look for a specific list of files to be skipped as they were determined to be on everyone's account and did not require migration. A list of these files can be found below.
The script then scans and exports information about each file the user account has in their account. 

The following information is added per file to the CSV:

-User

-Owner

-Filetype

-Size (in Bytes)

-Size (in MegaBytes)

-Timestamp of last modification

-If file is shared

The CSV is then filtered by Active/Inactive user accounts that were scanned.
The output can be found in the scripts default location as ‘TeamMemberFiles.csv’






Additional Script Arguments

‘--excluded_users’ or simplified ‘--e’ in combination with a filename can be added to exclude specific user account email addresses for users who have been preapproved to be excluded from the migration.
‘--user’ or simplified ‘--u’ in combination with a singular account email can be used just to export information on a singular user.
‘--batch_process_users’ or simplified ‘--b’ in combination with a filename can be added to export specific user account email addresses in bulk.



Files excluded in the script

The following files were considered to be on everyone's account by default and did not need to be migrated:

-ZS Tools & Utilities (1)

-ZS Tools & Utilities

-New Hire On-Boarding Reading

-New Hire Forms & Information

-SOP Link (1)

-Documents for Review (1)

-Documents for Review

-Get Started with Dropbox

Additionally several teams had editor/owner access to the shared location"/Market Access/" that also needed to be excluded in the scan.


Script location

When this script was last used it was living on a dedicated script server that was spun up as part of this massive file migration. Currently it lives as a redacted version of its former self on my github account.

https://github.com/VegaEX/Dropbox-File-info/blob/master/dropbox_file_management.py
