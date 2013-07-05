# -*- coding: utf-8 -*-
'''
Created on 2013-6-30

@author: dlash
'''
import ptnObject

PHYSICALID = '0x70.0a.10.08.0100101001.000000'

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

            item = ptnObject.ptn_item(data[2], data[1].replace('0x', ''), data[6], data[3])
            attr = item.setAttr(data[4], data[7], data[8], data[9])

            if ('C' in attr) and (tbl.getTblType() == 'Static'):
                tbl.setTblType('Dynamic')

            if not data[10] == '':
                item.setCombineId(data[10])
                tbl.combine_list.add(data[10])

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


