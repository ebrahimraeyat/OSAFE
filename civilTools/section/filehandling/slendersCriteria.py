# -*- coding: utf-8 -*-
import csv
import codecs
CODEC = "UTF-8"


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

class WriteSlenders(object):
    compositeDict = {}

    def __init__(self, fname):
        fh = codecs.open(unicode("slenders.py"), "w", CODEC)
        fh.write("# -*- coding: utf-8 -*-\n\n\nslenderParameters = {")
        with open(unicode(fname), 'rb') as stream:
            for comositeSection in ('notPlate', 'TBPlate', 'LRPlate'):
                fh.write("'{}':{{".format(comositeSection))
                for sectionPos in ('beam', 'column'):
                    fh.write("'{}':{{".format(sectionPos))
                    for ductility in ('M', 'H'):
                        fh.write("'{}':{{".format(ductility))
                        for rowdata in unicode_csv_reader(stream):
                            BF = rowdata[3]
                            tfCriteria = rowdata[4]
                            TF1 = rowdata[5]
                            TF2 = rowdata[6]
                            D = rowdata[7]
                            twCriteria = rowdata[8]
                            TW1 = rowdata[9]
                            TW2 = rowdata[10]

                            fh.write("'BF' : '{}', 'tfCriteria' : '{}', 'TF' : ('{}', '{}'), 'D' : '{}', 'twCriteria' : '{}', 'TW' : ('{}', '{}')}}\n".format(
                                    BF, tfCriteria, TF1, TF2, D, twCriteria, TW1, TW2))

            fh.write("}}}}")
            fh.close()

writeSlender = WriteSlenders("slendersParam.csv")


