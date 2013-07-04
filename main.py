# -*- coding: utf-8 -*-
'''
Created on 2013-6-30

@author: dlash
'''

PHYSICALID = '0x70.0a.01.08.0100101001.000000'

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
                        pkt_create_payload += '.%s%04d.%s' % (item_data[item]['id'], item_data[item]['length'], item)
                        length += item_data[item]['length'] + 1 + 2
                    pkt_create_payload = '%s.%04d%s' % (tbl_data['tbl_id'], length, pkt_create_payload)
                    length += 6
                    pkt_create_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_create_payload)
                    wf.write('  create:%s;%s;%s\n' % (pkt_create_fun, obj_idx, pkt_create_payload))
                    wf.write('  delete:%s;%s;60\n' % (pkt_create_fun, obj_idx))

                if not tbl_data['get'] == []:
                    pkt_get_fun = '0x30.07.10.05.%sFF' % tbl_data['tbl_id']
                    pkt_get_payload = ''
                    length = 0
                    for item in tbl_data['get']:
                        pkt_get_payload += '.%s.0000' % (item_data[item]['id'])
                        length += 1 + 2
                    pkt_get_payload = '%s.%04d%s' % (tbl_data['tbl_id'], length, pkt_get_payload)
                    length += 6
                    pkt_get_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_get_payload)

                    wf.write('  get all:%s;%s;%s\n' % (pkt_get_fun, PHYSICALID, pkt_get_payload))
                    if not tbl_data['index'] == []:
                        wf.write('  get:%s;%s;%s\n' % (pkt_get_fun, obj_idx, pkt_get_payload))
                    wf.write('\n')

                for item in tbl_data['item']:
                    if item_data[item]['set']:
                        length = 0
                        pkt_set_fun = '0x10.07.10.05.%s%s' % (tbl_data['tbl_id'], item_data[item]['id'])
                        pkt_set_payload = '%s.%04d.%s' % (item_data[item]['id'], item_data[item]['length'], item)
                        length += item_data[item]['length'] + 1 + 2
                        pkt_set_payload = '%s.%04d.%s' % (tbl_data['tbl_id'], length, pkt_set_payload)
                        length += 6
                        pkt_set_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_set_payload)
                        wf.write('  %s.set:%s;%s;%s\n' % (item, pkt_set_fun, obj_idx, pkt_set_payload))

                    if item_data[item]['get']:
                        length = 0
                        pkt_get_fun = '0x30.07.10.05.%s%s' % (tbl_data['tbl_id'], item_data[item]['id'])
                        pkt_get_payload = '%s.0000' % (item_data[item]['id'])
                        length += 1 + 2
                        pkt_get_payload = '%s.%04d.%s' % (tbl_data['tbl_id'], length, pkt_get_payload)
                        length += 6
                        pkt_get_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_get_payload)
                        wf.write('  %s.get:%s;%s;%s\n' % (item, pkt_get_fun, obj_idx, pkt_get_payload))

                    wf.write('\n')

                for combo_idx in tbl_data['combo']:
                    pkt_set_fun = '0x10.07.10.05.%s%s' % (tbl_data['tbl_id'], combo_idx)
                    pkt_set_payload = ''
                    wf.write('  0x%s(' % combo_idx),
                    for item in item_data[combo_idx]:
                        length = 0
                        pkt_set_payload += '.%s%04d.%s' % (item_data[item]['id'], item_data[item]['length'], item)
                        length += item_data[item]['length'] + 1 + 2
                        wf.write('%s,' % item),
                    pkt_set_payload = '%s.%04d.%s' % (tbl_data['tbl_id'], length, pkt_set_payload)
                    length += 6
                    pkt_set_payload = '0x60.%s.%s' % (genIdxLen(length), pkt_set_payload)
                    wf.write(').set:%s;%s;%s\n' % (pkt_set_fun, obj_idx, pkt_set_payload))

                    wf.write('\n')

            tbl_data = {}
            item_data = {}
            tbl_data['tbl_name'] = data[0]
            tbl_data['item'] = []
            tbl_data['create'] = []
            tbl_data['get'] = []
            tbl_data['index'] = []
            tbl_data['combo'] = []
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
                tbl_data['combo'].append(data[10])
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

if __name__ == '__main__':
    main('oam')
    main('aps')
    main('qos')
    main('acl')
    main('mpls')
