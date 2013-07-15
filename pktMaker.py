# -*- coding: utf-8 -*-
'''
Created on 2013-7-13

@author: dlash
'''

import ptnObject
from docGen import readXlsxFile
from docGen import MOD_LIST

def getIndex(tbl):
    string = ''
    for idx_item in [tbl.getTblItemDict()[i] for i in tbl.index_list]:
        string += '%s(%d),' % (idx_item.getItemName(), idx_item.getItemLen())
    input_idx_str = raw_input('please input the idx(%s):' % string)
    idx = input_idx_str.split(',')
    if len(idx) != len(tbl.index_list):
        raise

    obj_idx_str = ptnObject.genObjIdx(tbl.tbl_id, [tbl.item[item_id] for item_id in tbl.index_list], tbl.tbl_type, idx)

    return obj_idx_str

def getCreatePayload(tbl):
    string = ''
    for create_item in [tbl.getTblItemDict()[i] for i in tbl.create_list]:
        string += '%s(%d),' % (create_item.getItemName(), create_item.getItemLen())
    input_idx_str = raw_input('please input the value(%s):\n' % string)
    create = input_idx_str.split(',')
    if len(create) != len(tbl.create_list):
        raise

    create_payload_str = ptnObject.genPayload(tbl.tbl_id, [tbl.item[item_id] for item_id in tbl.create_list], 'set', create)

    return create_payload_str

def processPkt(tbl, func):

    obj_idx = getIndex(tbl)
    if func == 'delete':
        fun_idx = tbl.getPkt()['create.fun_idx']
        payload = '0x60'
    elif func == 'create':
        fun_idx = tbl.getPkt()['create.fun_idx']
        payload = getCreatePayload(tbl)
    elif func == 'get':
        fun_idx = tbl.getPkt()['get.fun_idx']
        payload = tbl.getPkt()['get.payload']
    elif func == 'get_all':
        fun_idx = tbl.getPkt()['get.fun_idx']
        obj_idx = u'0x70.0a.10.08.0100101001.000000'
        payload = tbl.getPkt()['get.payload']
    else:
        raise

    print('function_index:%s' % fun_idx)
    print('object_index:%s' % obj_idx)
    print('payload:%s' % payload)


def processTable(tbl):
    fun_list = []
    tbl.genPackets()

    fun_list.append('get')
    if tbl.getPkt().has_key('create.fun_idx'):
        fun_list.append('create')
        fun_list.append('delete')
        fun_list.append('get_all')

    fun_list.sort()

    while(1):
        print('Which packet do u want:')
        for i, fun in enumerate(fun_list):
            print('%d:%s' % (i + 1, fun))

        in_str = raw_input('Enter the number(q for quit):')
        if in_str.lower() == 'q':
            break
        else:
#             try:
                i = int(in_str) - 1
                print('%s:' % fun_list[i])
                processPkt(tbl, fun_list[i])
#             except:
#                 print('3Wrong input!')

    return

def processModule(mod):
    while(1):
        print('Select Table:')
        for i, tbl in enumerate(mod):
            print('%d:%s' % (i + 1, tbl.getTblName()))

        in_str = raw_input('Enter the number(q for quit):')
        if in_str.lower() == 'q':
            break
        else:
#             try:
                i = int(in_str) - 1
                print('%s' % mod[i].getTblName())
                processTable(mod[i])
#             except:
#                 print('2Wrong input!')

    return

def pktMaker():
    module_obj = readXlsxFile('demo')
    while(1):
        print('Module List:')
        for i, mod_name in enumerate(MOD_LIST):
            print('%d:%s' % (i + 1, mod_name))

        in_str = raw_input('Enter the number(q for quit):')
        if in_str.lower() == 'q':
            break
        else:
#             try:
                i = int(in_str) - 1
                print('%s' % MOD_LIST[i])
                processModule(module_obj[MOD_LIST[i]])
#             except:
#                 print('1Wrong input!')

    return

if __name__ == '__main__':
    pktMaker()
