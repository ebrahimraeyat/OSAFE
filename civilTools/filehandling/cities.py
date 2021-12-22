# -*- coding: utf-8 -*-
import csv
import codecs
CODEC = "UTF-8"


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

class WriteOstan(object):
    ostandDict = {}

    def __init__(self, fname):
        fh = codecs.open(unicode("city.py"), "w", CODEC)
        fh.write("# -*- coding: utf-8 -*-\n\n\nostans = {")
        with open(unicode(fname), 'rb') as stream:
            for rowdata in unicode_csv_reader(stream):
                #ostans = {esfehan:{ali:[1,2], ebi:[1, 10]},
                #yazd:{meybod:[1,2], ardakan:[3,2]}}
                ostan = rowdata[0]
                shahr = rowdata[1]
                khatar = rowdata[2]
                radif = rowdata[3]
                if not ostan in WriteOstan.ostandDict.keys():
                    fh.write('},\n')
                    fh.write('u"%s":\n\t{u"%s": [%s, %s]' % (ostan, shahr, khatar, radif))
                else:
                    fh.write(',\n\tu"%s": [%s, %s]' % (shahr, khatar, radif))
                WriteOstan.ostandDict[ostan] = 1

            fh.write("}}")
            fh.close()

writeOstan = WriteOstan("ostans.csv")
#loadFile("ostans.csv")

