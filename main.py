# -*- coding: utf-8 -*-
'''
Created on 2013-6-30

@author: dlash
'''
import ptnObject

PHYSICALID = '0x70.0a.10.08.0100101001.000000'

def main(f_name):
    f = open('%s.csv' % f_name)
    wf = open('%s_out.txt' % f_name, 'w')
    tbl_data = {}
    item_data = {}

    for line in f:
        data = line.split(',')

        if data[1] == '':
            if not tbl_data == {}:
                wf.write('\n%s:\n' % tbl_data['tbl_name'])

                obj_idx = ''
                length = 0
                for item in tbl_data['index']:
                    if item == tbl_data['index'][-1]:
                        obj_type = '10'
                        if not tbl_data['create'] == []:
                            obj_type = '30'
                        obj_idx += '%s.%s.%s%s.%s' % (obj_type, genIdxLen(item_data[item]['length'] + 5), tbl_data['tbl_id'], item_data[item]['id'], item)
                    else:
                        obj_type = '00'
                        if not tbl_data['create'] == []:
                            obj_type = '20'
                        obj_idx += '%s.%s.%s%s.%s.' % (obj_type, genIdxLen(item_data[item]['length'] + 5), tbl_data['tbl_id'], item_data[item]['id'], item)
                    length += item_data[item]['length'] + 5 + len(genIdxLen(item_data[item]['length'] + 5)) / 2 + 1

                if length == 0:
                    obj_idx = PHYSICALID
                else:
                    obj_idx = '0x70.%s.00.08.0100101001.000000.%s' % (genIdxLen(length + 10), obj_idx)

                if not tbl_data['create'] == []:
                    pkt_create_fun = '0x11.07.10.05.%sFF' % tbl_data['tbl_id']
                    pkt_create_payload = ''
                    length = 0
                    for item in tbl_data['create']:
                        pkt_create_payload += '.%s%04x.%s' % (item_data[item]['id'], (item_data[item]['length'] + 0x8000), item)
                        length += item_data[item]['length'] + 1 + 2
                    pkt_create_payload = '%s.%04x%s' % (tbl_data['tbl_id'], (length + 0x8000), pkt_create_payload)
                    length += 6
                    pkt_create_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_create_payload)
                    wf.write('create:\n%s\n%s\n%s\n' % (pkt_create_fun, obj_idx, pkt_create_payload))
                    wf.write('create raw:\n%s\n%s\n%s\n' % (pkt_create_fun.replace('.', ''), obj_idx.replace('.', ''), pkt_create_payload.replace('.', '')))
                    wf.write('delete:\n%s\n%s\n0x60\n' % (pkt_create_fun, obj_idx))
                    wf.write('delete raw:\n%s\n%s\n0x60\n' % (pkt_create_fun.replace('.', ''), obj_idx.replace('.', '')))

                if not tbl_data['get'] == []:
                    pkt_get_fun = '0x30.07.10.05.%sFF' % tbl_data['tbl_id']
                    pkt_get_payload = ''
                    length = 0
                    for item in tbl_data['get']:
                        pkt_get_payload += '.%s.8000' % (item_data[item]['id'])
                        length += 1 + 2
                    pkt_get_payload = '%s.%04x%s' % (tbl_data['tbl_id'], (length + 0x8000), pkt_get_payload)
                    length += 6
                    pkt_get_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_get_payload)

                    wf.write('get all:\n%s\n%s\n%s\n' % (pkt_get_fun, PHYSICALID, pkt_get_payload))
                    wf.write('get all raw:\n%s\n%s\n%s\n' % (pkt_get_fun.replace('.', ''), PHYSICALID.replace('.', ''), pkt_get_payload.replace('.', '')))
                    if not tbl_data['index'] == []:
                        wf.write('get:\n%s\n%s\n%s\n' % (pkt_get_fun, obj_idx, pkt_get_payload))
                        wf.write('get raw:\n%s\n%s\n%s\n' % (pkt_get_fun.replace('.', ''), obj_idx.replace('.', ''), pkt_get_payload.replace('.', '')))
                    wf.write('\n')

                for item in tbl_data['item']:
                    if item_data[item]['set']:
                        length = 0
                        pkt_set_fun = '0x10.07.10.05.%s%s' % (tbl_data['tbl_id'], item_data[item]['id'])
                        pkt_set_payload = '%s.%04x.%s' % (item_data[item]['id'], (item_data[item]['length'] + 0x8000), item)
                        length += item_data[item]['length'] + 1 + 2
                        pkt_set_payload = '%s.%04x.%s' % (tbl_data['tbl_id'], (length + 0x8000), pkt_set_payload)
                        length += 6
                        pkt_set_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_set_payload)
                        wf.write('%s.set:\n%s\n%s\n%s\n' % (item, pkt_set_fun, obj_idx, pkt_set_payload))
                        wf.write('%s.set raw:\n%s\n%s\n%s\n' % (item, pkt_set_fun.replace('.', ''), obj_idx.replace('.', ''), pkt_set_payload.replace('.', '')))

                    if item_data[item]['get']:
                        length = 0
                        pkt_get_fun = '0x30.07.10.05.%s%s' % (tbl_data['tbl_id'], item_data[item]['id'])
                        pkt_get_payload = '%s.8000' % (item_data[item]['id'])
                        length += 1 + 2
                        pkt_get_payload = '%s.%04x.%s' % (tbl_data['tbl_id'], (length + 0x8000), pkt_get_payload)
                        length += 6
                        pkt_get_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_get_payload)
                        wf.write('%s.get:\n%s\n%s\n%s\n' % (item, pkt_get_fun, obj_idx, pkt_get_payload))
                        wf.write('%s.get raw:\n%s\n%s\n%s\n' % (item, pkt_get_fun.replace('.', ''), obj_idx.replace('.', ''), pkt_get_payload.replace('.', '')))

                    wf.write('\n')

                for combo_idx in tbl_data['combo']:
                    pkt_set_fun = '0x10.07.10.05.%s%s' % (tbl_data['tbl_id'], combo_idx)
                    pkt_set_payload = ''
                    wf.write('0x%s.set(' % combo_idx),
                    for item in item_data[combo_idx]:
                        length = 0
                        pkt_set_payload += '.%s%04x.%s' % (item_data[item]['id'], (item_data[item]['length'] + 0x8000), item)
                        length += item_data[item]['length'] + 1 + 2
                        wf.write('%s,' % item),
                    wf.write(')\n')
                    pkt_set_payload = '%s.%04x%s' % (tbl_data['tbl_id'], (length + 0x8000), pkt_set_payload)
                    length += 6
                    pkt_set_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_set_payload)
                    wf.write('%s\n%s\n%s\n' % (pkt_set_fun, obj_idx, pkt_set_payload))
                    wf.write('raw:\n%s\n%s\n%s\n' % (pkt_set_fun.replace('.', ''), obj_idx.replace('.', ''), pkt_set_payload.replace('.', '')))

                    wf.write('\n')

            tbl_data = {}
            item_data = {}
            tbl_data['tbl_name'] = data[0]
            tbl_data['item'] = []
            tbl_data['create'] = []
            tbl_data['get'] = []
            tbl_data['index'] = []
            tbl_data['combo'] = set()
        elif data[0][:2].lower() == '0x':
            data = data[:11]
            if not tbl_data.has_key('tbl_id'):
                tbl_data['tbl_id'] = data[0].replace('0x', '')

            tbl_data['item'].append(data[2])
            item_data[data[2]] = {'id':data[1].replace('0x', ''), 'set':0, 'get':0, 'length':int(data[6])}

            if not data[4] == '0':
                tbl_data['index'].append(data[2])

            if data[7] == '1':
                item_data[data[2]]['set'] = 1

            if data[9] == '1':
                item_data[data[2]]['get'] = 1
                tbl_data['get'].append(data[2])

            if data[8] == '1':
                tbl_data['create'].append(data[2])

            if not data[10].strip() == '':
                item_data[data[2]]['set'] = 0
                tbl_data['combo'].add(data[10])
                if item_data.has_key(data[10]):
                    item_data[data[10]].append(data[2])
                else:
                    item_data[data[10]] = [data[2]]

    wf.close()
    f.close()
    pass

def genIdxLen(length):
    if length < 0x80:
        return '%02x' % length
    elif length < 0x4000:
        return '%04x' % (length + 0x8000)
    elif length < 0x200000:
        return '%06x' % (length + 0xc00000)
    elif length < 0x10000000:
        return '%08x' % (length + 0xe0000000)

def readCsvFile(name):
    f = open('%s.csv' % name)
    tbl = None
    tbl_list = []

    for line in f:
        data = [x.strip() for x in line.split(',')]

        if data[1] == '':
            if not tbl == None:
                tbl_list.append(tbl)

            tbl = ptnObject.ptn_table(data[0])
        elif data[0][:2].lower() == '0x':
            data = data[:11]
            if tbl.getTblId() == '':
                tbl.setTblId(data[0].replace('0x', ''))

            item = ptnObject.ptn_item(data[2], data[1].replace('0x', ''), data[6])
            attr = item.setAttr(data[4], data[7], data[8], data[9])

            if ('C' in attr) and (tbl.getTblType() == 'Static'):
                tbl.setTblType('Dynamic')

            if not data[10] == '':
                item.setCombineId(data[10])

            tbl.addItem(item)
        else:
            print(line)
            continue

    f.close()
    return tbl_list

def writeTxtFile(tbl_list, fname):
    f = open('%sout.txt' % fname, 'w')

    for tbl in tbl_list:
        tbl.genPackets()
        pkt = tbl.getPkt()
        f.write('\n%s:\n' % tbl.getTblName())
        if tbl.getTblType() == 'Dynamic':
            f.write('Create:\n%s\n%s\n%s\n' % (pkt['create.fun_idx'], pkt['obj_idx'], pkt['create.payload']))
            f.write('Create raw:\n%s\n%s\n%s\n' % (pkt['create.fun_idx'].replace('.', ''), pkt['obj_idx'].replace('.', ''), pkt['create.payload'].replace('.', '')))
            f.write('Delete:\n%s\n%s\n0x60\n' % (pkt['create.fun_idx'], pkt['obj_idx']))
            f.write('Delete raw:\n%s\n%s\n0x60\n' % (pkt['create.fun_idx'].replace('.', ''), pkt['obj_idx'].replace('.', '')))

            f.write('Get_all:\n%s\n%s\n%s\n' % (pkt['get.fun_idx'], PHYSICALID, pkt['get.payload']))
            f.write('Get_all raw:\n%s\n%s\n%s\n' % (pkt['get.fun_idx'].replace('.', ''), PHYSICALID.replace('.', ''), pkt['get.payload'].replace('.', '')))

        f.write('Get:\n%s\n%s\n%s\n' % (pkt['get.fun_idx'], pkt['obj_idx'], pkt['get.payload']))
        f.write('Get raw:\n%s\n%s\n%s\n\n\n' % (pkt['get.fun_idx'].replace('.', ''), pkt['obj_idx'].replace('.', ''), pkt['get.payload'].replace('.', '')))

        for item in tbl.getTblItem():
            pkt_item = item.getPkt()

            if 'M' in item.getAttr():
                f.write('%s.set:\n%s\n%s\n%s\n' % (item.getItemName(), pkt_item['set.fun_idx'], pkt['obj_idx'], pkt_item['set.payload']))
                f.write('%s.set raw:\n%s\n%s\n%s\n' % (item.getItemName(), pkt_item['set.fun_idx'].replace('.', ''), pkt['obj_idx'].replace('.', ''), pkt_item['set.payload'].replace('.', '')))
            if 'R' in item.getAttr():
                f.write('%s.get:\n%s\n%s\n%s\n' % (item.getItemName(), pkt_item['get.fun_idx'], pkt['obj_idx'], pkt_item['get.payload']))
                f.write('%s.get raw:\n%s\n%s\n%s\n' % (item.getItemName(), pkt_item['get.fun_idx'].replace('.', ''), pkt['obj_idx'].replace('.', ''), pkt_item['get.payload'].replace('.', '')))

            f.write('\n')

        for comb_idx in tbl.combine_list:
            f.write('combine_idx:0x%s.set:\n%s\n%s\n%s\n' % (comb_idx, pkt['%s.fun_idx' % comb_idx], pkt['obj_idx'], pkt['%s.payload' % comb_idx]))
            f.write('combine_idx:0x%s.set:\n%s\n%s\n%s\n\n' % (comb_idx, pkt['%s.fun_idx' % comb_idx].replace('.', ''), pkt['obj_idx'].replace('.', ''), pkt['%s.payload' % comb_idx].replace('.', '')))

    f.close()

if __name__ == '__main__':
    mod_list = ['mpls', 'qos', 'acl', 'aps', 'oam']

    for mod in mod_list:
        writeTxtFile(readCsvFile(mod), mod)


