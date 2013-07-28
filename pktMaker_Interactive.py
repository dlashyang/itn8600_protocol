# -*- coding: utf-8 -*-
'''
Created on 2013-7-13

@author: dlash
'''

import ptnObject
from docGen import readXlsxFile
from docGen import MOD_LIST

def getIndex(tbl):
    if len(tbl.index_list) == 0:
        return u'0x70.0a.10.08.0100101001.000000'

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

def getSetPayload(tbl, item):
    string = '%s(%d)' % (item.getItemName(), item.getItemLen())
    input_str = raw_input('please input the value(%s):' % string)

    payload_str = ptnObject.genPayload(tbl.tbl_id, [item], 'set', [input_str])

    return payload_str

def processItemSetPkt(tbl, func, obj_idx):
    item_list = tbl.getTblItemList_all()

    while (1):
        print('\n')
        for i, item in enumerate(item_list):
            if 'M' in item.getAttr():
                print('%d:%s' % (i + 1, item.getItemName()))

        in_str = raw_input('Which do u want(e for back, q for quit):')
        if in_str.lower() == 'q':
            exit()
        if in_str.lower() == 'e':
            break
        else:
#             try:
                i = int(in_str)
                item = item_list[i - 1]
                fun_idx = item.getPkt()['set.fun_idx']
                payload = getSetPayload(tbl, item)
#             except:
#                 print('3Wrong input!')

        print('Set for item %s' % item.getItemName())
        print('function_index:%s' % fun_idx)
        print('object_index:%s' % obj_idx)
        print('payload:%s' % payload)

    return

def processItemGetPkt(tbl, func, obj_idx):
    item_list = tbl.getTblItemList_all()

    while (1):
        print('\n')
        print('0:Table')
        for i, item in enumerate(item_list):
            if 'R' in item.getAttr():
                print('%d:%s' % (i + 1, item.getItemName()))

        in_str = raw_input('Which do u want(e for back, q for quit):')
        if in_str.lower() == 'q':
            exit()
        if in_str.lower() == 'e':
            break
        else:
#             try:
                i = int(in_str)
                if i == 0:
                    fun_idx = tbl.getPkt()['get.fun_idx']
                    payload = tbl.getPkt()['get.payload']
                else:
                    item = item_list[i - 1]
                    fun_idx = item.getPkt()['get.fun_idx']
                    payload = item.getPkt()['get.payload']
#             except:
#                 print('3Wrong input!')

        print('Get for item %s' % item.getItemName())
        print('function_index:%s' % fun_idx)
        print('object_index:%s' % obj_idx)
        print('payload:%s' % payload)

    return

def processTblPkt(tbl, func):
    fun_idx = ''
    payload = ''
    obj_idx = getIndex(tbl)

    if func == 'set':
        processItemSetPkt(tbl, func, obj_idx)
        return
    elif func == 'get':
        processItemGetPkt(tbl, func, obj_idx)
        return

    if func == 'delete':
        fun_idx = tbl.getPkt()['create.fun_idx']
        payload = '0x60'
    elif func == 'create':
        fun_idx = tbl.getPkt()['create.fun_idx']
        payload = getCreatePayload(tbl)
    elif func == 'get_all':
        fun_idx = tbl.getPkt()['get.fun_idx']
        payload = tbl.getPkt()['get.payload']
    else:
        raise

    print('%s for table' % func)
    print('function_index:%s' % fun_idx)
    print('object_index:%s' % obj_idx)
    print('payload:%s' % payload)
    return


def processTable(tbl):
    fun_list = []
    tbl.genPackets()

    fun_list.append('set')
    fun_list.append('get')
    if tbl.getPkt().has_key('create.fun_idx'):
        fun_list.append('create')
        fun_list.append('delete')
        fun_list.append('get_all')

    fun_list.sort()

    while(1):
        print('\n')
        for i, fun in enumerate(fun_list):
            print('%d:%s' % (i + 1, fun))

        in_str = raw_input('Which do u want(e for back, q for quit):')
        if in_str.lower() == 'q':
            exit()
        if in_str.lower() == 'e':
            break
        else:
#             try:
                i = int(in_str) - 1
                print('operation is %s:' % fun_list[i])
                processTblPkt(tbl, fun_list[i])
#             except:
#                 print('3Wrong input!')

    return

def processModule(mod):
    while(1):
        print('\n')
        for i, tbl in enumerate(mod):
            print('%d:%s' % (i + 1, tbl.getTblName()))

        in_str = raw_input('Which do u want(e for back, q for quit):')
        if in_str.lower() == 'q':
            exit()
        if in_str.lower() == 'e':
            break
        else:
#             try:
                i = int(in_str) - 1
                print('Table is %s' % mod[i].getTblName())
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
            exit()
        if in_str.lower() == 'e':
            break
        else:
#             try:
                i = int(in_str) - 1
                print('module is %s' % MOD_LIST[i])
                processModule(module_obj[MOD_LIST[i]])
#             except:
#                 print('1Wrong input!')

    return

if __name__ == '__main__':
    pktMaker()
