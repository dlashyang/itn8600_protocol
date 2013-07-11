# -*- coding: utf-8 -*-
'''
Created on 2013-6-30

@author: dlash
'''
import ptnObject
import xlrd
from xml.dom import minidom
from codecs import lookup

#MOD_LIST = ['mpls', 'qos', 'acl', 'aps', 'oam']
MOD_LIST = ['MPLS-TP', 'Qos', 'ACL', 'APS', 'OAM', 'L2']
PHYSICALID = '0x70.0a.10.08.0100101001.000000'

def readCsvFile(name):
    f = open('%s.csv' % name)
    tbl = None
    tbl_list = []

    for line in f:

#        line = unicode(line, 'gbk')
        data = [x.strip() for x in line.split(',')]

        if data[1] == '':
            if not tbl == None:
                tbl_list.append(tbl)

            tbl = ptnObject.ptn_table(data[0])
        elif data[0][:2].lower() == '0x':
            data = data[:11]
            if tbl.getTblId() == '':
                tbl.setTblId(data[0].replace('0x', ''))

            item_id = data[1].replace('0x', '')
            tbl.addItem(data[2], item_id, data[6], data[3])
            tbl.setItemAttr(item_id, data[4], data[7], data[8], data[9])

            if not data[10] == '':
                tbl.addCombineIdx(data[10].replace('0x', ''), item_id)

        else:
            print(line)
            continue
        
    del data

    f.close()
    return tbl_list

def readXlsxFile(name):
    f = xlrd.open_workbook('%s.xlsx' % name)
    module_list = {}

    for sheet_name in MOD_LIST:
        sheet = f.sheet_by_name(sheet_name)
        tbl = None
        tbl_list = []
    
        for i in range(sheet.nrows):
            data = sheet.row_values(i)
    
            if data[1] == '':
                if tbl != None and tbl.tbl_id != '' and data[0]:
                    tbl_list.append(tbl)
    
                tbl = ptnObject.ptn_table(data[0])

            elif str(data[0])[:2].lower() == '0x':
                if sheet.ncols == 14:
                    data = data[:11]
                elif sheet.ncols == 15:
                    data = data[:12]
                    data.pop(3)

                if tbl.getTblId() == '':
                    tbl.setTblId(data[0].replace('0x', ''))
    
                item_id = data[1].replace('0x', '')
                tbl.addItem(data[2], item_id, data[6], data[3])
                tbl.setItemAttr(item_id, data[4], data[7], data[8], data[9])

                if data[10]:
                    tbl.addCombineIdx(data[10], item_id)
    
            else:
                print(data)
                continue

        tbl_list.append(tbl)
        module_list[sheet_name] = tbl_list

    return module_list


def writeTxtFile(tbl_list, fname):
    f = open('%sout.txt' % fname, 'w')

    for tbl in tbl_list:
        tbl.genPackets()
        pkt = tbl.getPkt()
        f.write('\n%s:\n' % tbl.getTblName())
        if tbl.getTblType() == 'Dynamic' and tbl.create_list != []:
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

def genPktNode(dom, node_name, fun_idx, obj_idx, payload):
    node = dom.createElement(node_name)
    node_pkt = dom.createElement('function_index')
    packet = dom.createTextNode('%s' % fun_idx)
    node_pkt.appendChild(packet)
    node.appendChild(node_pkt)

    node_pkt = dom.createElement('raw_packet')
    packet = dom.createTextNode('%s' % fun_idx.replace('.', ''))
    node_pkt.appendChild(packet)
    node.appendChild(node_pkt)

    node_pkt = dom.createElement('object_index')
    packet = dom.createTextNode('%s' % obj_idx)
    node_pkt.appendChild(packet)
    node.appendChild(node_pkt)

    node_pkt = dom.createElement('raw_packet')
    packet = dom.createTextNode('%s' % obj_idx.replace('.', ''))
    node_pkt.appendChild(packet)
    node.appendChild(node_pkt)

    node_pkt = dom.createElement('payload')
    packet = dom.createTextNode('%s' % payload)
    node_pkt.appendChild(packet)
    node.appendChild(node_pkt)

    node_pkt = dom.createElement('raw_packet')
    packet = dom.createTextNode('%s' % payload.replace('.', ''))
    node_pkt.appendChild(packet)
    node.appendChild(node_pkt)

    return node

def genXml():
    dom = minidom.getDOMImplementation().createDocument(None, 'DataSpec', None)
    root = dom.documentElement
    module = readXlsxFile('V1.7.1')

    for mod in MOD_LIST:
        node_mod = dom.createElement('Module')
        node_mod.setAttribute('mod_name', '%s' % mod)

        for tbl in module[mod]:
            tbl.genPackets()
            tbl.dbg_print()
            node_table = dom.createElement('Table')
            node_table.setAttribute('table_name', '%s' % tbl.getTblName())
            node_table.setAttribute('table_id', '%s' % tbl.getTblId())

            tbl_pkt = tbl.getPkt()
            if tbl_pkt.has_key('create.fun_idx'):
                node = genPktNode(dom, 'Create', tbl.pkt['create.fun_idx'], tbl.pkt['obj_idx'], tbl.pkt['create.payload'])
                node_table.appendChild(node)

                node = genPktNode(dom, 'Delete', tbl.pkt['create.fun_idx'], tbl.pkt['obj_idx'], '0x60')
                node_table.appendChild(node)

            if tbl_pkt.has_key('get.fun_idx'):
                node = genPktNode(dom, 'Get', tbl.pkt['get.fun_idx'], tbl.pkt['obj_idx'], tbl.pkt['get.payload'])
                node_table.appendChild(node)

            for item in tbl.getTblItem():
                item.dbg_print()
                pkt_item = item.getPkt()
                node_item = dom.createElement('Item')
                node_item.setAttribute('item_name', '%s' % item.getItemName())
                node_item.setAttribute('item_id', '%s' % item.getItemId())

                print ('%s:%s' % (type(item.getAttr()), item.getAttr()))
                if 'M' in item.getAttr():
                    node = genPktNode(dom, 'Set', pkt_item['set.fun_idx'], tbl.pkt['obj_idx'], pkt_item['set.payload'])
                    node_item.appendChild(node)
                if 'R' in item.getAttr():
                    node = genPktNode(dom, 'Get', pkt_item['get.fun_idx'], tbl.pkt['obj_idx'], pkt_item['get.payload'])
                    node_item.appendChild(node)

                node_table.appendChild(node_item)

            node_mod.appendChild(node_table)

        root.appendChild(node_mod)

    f = open('Packets.xml', 'w')
    writer = lookup('utf-8')[3](f)
    dom.writexml(writer, indent="  ", addindent="    ", newl="\n", encoding='utf-8')
    writer.close()

if __name__ == '__main__':
#    for mod in MOD_LIST:
#        writeTxtFile(readCsvFile(mod), mod)

    genXml()


