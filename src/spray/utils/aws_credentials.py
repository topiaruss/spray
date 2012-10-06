"""
Look in ProjectRoot/etc for credential files by name and
return Access Key Id and Secret Access Key as tuple

Format of the files is defined by Amazon's csv download format.
Example:

"User Name","Access Key Id","Secret Access Key"
"Joan Johns","xxxidxxx","yyykeyyyy"

"""
import os
import csv
try:
    import settings
    STATIC_PATH = None
except:
    candidates = ['etc/spray.client.csv',
      os.path.abspath('./../../../etc/spray.client.csv')]
    STATIC_PATH = [p for p in candidates if os.path.exists(p)][0]

first_pass_only = [1]


def get_credentials(filename):
    "let's not force an extension on the parameter... flexibility, later"
    path = STATIC_PATH or \
      os.path.join(settings.SITE_ROOT, 'etc', filename + '.csv')
    if first_pass_only:
        print 'credentials source from: %s' % path
        del first_pass_only[0]
    with open(path, 'rb') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',', quotechar='"')

        # check the format has not changed
        hdrs = rdr.next()
        assert hdrs[0] == 'User Name'

        #get the data
        data = rdr.next()

        # let's keep it sane. Filename must match User Name, and that's that
        assert data[0] == filename

        return (data[1:])
