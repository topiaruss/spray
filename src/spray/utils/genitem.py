# genitem.py
#
# Concatenate multiple generators into a single sequence

import simplejson as json

def gen_items(ifiles):
    for ifile in ifiles:
        items = json.load(ifile)
        for i in items:
            yield i

# Example use

if __name__ == '__main__':
    tfile = file('/tmp/genitem.tst', 'w')
    items = [1,2,3]
    json.dump(items, tfile)
    tfile.close()

    items = gen_items(file('/tmp/genitem.tst', 'r'))
    for item in items:
        print item,