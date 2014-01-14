from django.conf import settings


def get_credentials():
    return settings.SPRAY_SETTINGS['CREDENTIALS']

#
# """
# Look in ProjectRoot/etc for credential files by name and
# return Access Key Id and Secret Access Key as tuple
#
# Format of the files is defined by Amazon's csv download format.
# Example:
#
# "User Name","Access Key Id","Secret Access Key"
# "Joan Johns","xxxidxxx","yyykeyyyy"
#
# """
# import os
# import csv
#
# try:
#     import settings
#     STATIC_PATH = None
# except:
#     curdir = os.path.abspath('.')
#     while not curdir.endswith('spray'):
#         curdir = os.path.split(curdir)[0]
#         print 'going up a dir to %s' % curdir
#     candidates = ['scraft.spray.client.csv', 'spray.client.csv']
#     for c in candidates:
#         csvfile = os.path.join(curdir, 'etc', c)
#         print 'checking %s for csv file' % csvfile
#         if os.path.exists(csvfile):
#             STATIC_PATH = csvfile
#             break
#
# first_pass_only = [1]

# def get_credentials(filename):
    # "let's not force an extension on the parameter... flexibility, later"
    # path = STATIC_PATH or os.path.join(settings.SITE_ROOT, 'etc', filename + '.csv')
    # if first_pass_only:
    #     print 'credentials source from: %s' % path
    #     del first_pass_only[0]
    #
    # with open(path, 'rb') as csvfile:
    #     rdr = csv.reader(csvfile, delimiter=',', quotechar='"')
    #
    #     # check the format has not changed
    #     hdrs = rdr.next()
    #     assert hdrs[0] == 'User Name'
    #
    #     #get the data
    #     data = rdr.next()
    #
    #     return (data[1:])
