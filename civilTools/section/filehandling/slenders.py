# -*- coding: utf-8 -*-


slenderParameters = {'notPlate': {'beam': {'M': {'BF': '2*bf', 'tfCriteria': True, 'TF': ('2*tf', ''), 'D': 'd',
                    'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')},
                    'H': {'BF': '2*bf', 'tfCriteria': True, 'TF': ('2*0.55*tf/.6', ''), 'D': 'd',
                    'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')}},
                                'column': {'M': {'BF': '2*bf', 'tfCriteria': True, 'TF': ('2*tf', ''), 'D': 'd',
                                'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')},
                                'H': {'BF': '2*bf', 'tfCriteria': True, 'TF': ('2*tf', ''), 'D': 'd',
                                'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')}}},
                    'TBPlate': {'beam': {'M': {'BF': 'c+bf', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                    'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                    'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')},
                    'H': {'BF': 'c+bf', 'tfCriteria': 't1<(.6*B1*tf)/(0.55*bf)',
                        'TF': ('(0.55*BF*t1)/(.60*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')}},
                    'column': {'M': {'BF': 'c+bf', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                    'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                    'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')},
                        'H': {'BF': 'c+bf', 'tfCriteria': 't1<(B1*tf)/(bf)',
                            'TF': ('(BF*t1)/(B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                            'twCriteria': True, 'TW': ('(D-2*TF)/(d-2(tf+r))*tw', '')}}},
                    'LRPlate': {'beam': {'M': {'BF': 'c+bf+2*tf', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                        'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                        'H': {'BF': 'c+bf+2*tf', 'tfCriteria': 't1<(.6*B1*tf)/(0.55*bf)',
                        'TF': ('(0.55*BF*t1)/(.60*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}},
                        'column': {'M': {'BF': 'c+bf+2*tf', 'tfCriteria': 't1<(.76*B1*tf)/(1.12*bf)',
                        'TF': ('(1.12*BF*t1)/(.76*B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')},
                        'H': {'BF': 'c+bf+2*tf', 'tfCriteria': 't1<(B1*tf)/(bf)',
                        'TF': ('(BF*t1)/(B1)', '(BF*tf)/bf'), 'D': 'd+2*t1',
                        'twCriteria': 't2<(d*tw)/(d-2(tf+r))', 'TW': ('t2*(D-2*TF)/d', 'tw*(D-2*TF)/(d-2*(tf+r))')}}}}

if __name__ == '__main__':
    comositeSection = 'LRPlate'
    sectionPos = 'beam'
    ductility = 'M'
    parameters = slenderParameters[comositeSection][sectionPos][ductility]
    BF = parameters['BF']
    tfCriteria = parameters['tfCriteria']
    TF1 = parameters['TF'][0]
    TF2 = parameters['TF'][1]
    D = parameters['D']
    twCriteria = parameters['twCriteria']
    TW1 = parameters['TW'][0]
    TW2 = parameters['TW'][1]

    print BF
    print tfCriteria