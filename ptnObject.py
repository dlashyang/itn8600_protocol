'''
Created on 2013-7-3

@author: dlash
'''

PHYSICALID = '10.08.0100101001.000000'
ITEM_ID_LEN = 1
TABLE_ID_LEN = 4
PAYLOAD_LENGTH_LEN = 2

class ptn_table(object):
    '''
    classdocs
    '''

    def __init__(self, name):
        self.tbl_name = name
        self.tbl_id = ''
        self.tbl_type = 'Static'
        self.tbl_idx = []
        self.item = []
        self.pkt = {}
        self.combine_list = set()

    def addItem(self, item):
        self.item.append(item)

    def setTblId(self, tblid):
        self.tbl_id = tblid

    def getTblId(self):
        return self.tbl_id

    def setTblType(self, tbl_type):
        self.tbl_type = tbl_type

    def getTblType(self):
        return self.tbl_type

    def getTblItem(self):
        return self.item

    def getTblName(self):
        return self.tbl_name

    def getPkt(self):
        return self.pkt

    def genPackets(self):
        create_list = []
        index_list = []
        get_list = []
        combine_item = {}

        for comb_idx in self.combine_list:
            combine_item[comb_idx] = []

        for item in self.item:
            if 'C' in item.getAttr():
                create_list.append(item)

            if 'I' in item.getAttr():
                index_list.append(item)

            if 'M' in item.getAttr():
                item.setPkt('set.fun_idx', genFunIdx(self.tbl_id, item.getItemId(), 'set'))
                item.setPkt('set.payload', genPayload(self.tbl_id, [item], 'set'))

            if 'R' in item.getAttr():
                get_list.append(item)
                item.setPkt('get.fun_idx', genFunIdx(self.tbl_id, item.getItemId(), 'get'))
                item.setPkt('get.payload', genPayload(self.tbl_id, [item], 'get'))

            if not item.combine_id == '':
                combine_item[item.combine_id].append(item)

        self.pkt['obj_idx'] = genObjIdx(self.tbl_id, index_list, self.tbl_type)
        self.pkt['create.fun_idx'] = genFunIdx(self.tbl_id, 'FF', 'create')
        self.pkt['create.payload'] = genPayload(self.tbl_id, create_list, 'set')
        self.pkt['get.fun_idx'] = genFunIdx(self.tbl_id, 'FF', 'get')
        self.pkt['get.payload'] = genPayload(self.tbl_id, get_list, 'get')

        for comb_idx in self.combine_list:
            self.pkt['%s.fun_idx' % comb_idx] = genFunIdx(self.tbl_id, comb_idx, 'set')
            self.pkt['%s.payload' % comb_idx] = genPayload(self.tbl_id, combine_item[comb_idx], 'set')

class ptn_item(object):
    '''
    classdocs
    '''

    def __init__(self, name, item_id, item_len, item_type):
        self.item_name = name
        self.item_id = item_id
        self.item_len = int(item_len)
        self.item_type = item_type
        self.combine_id = ''
        self.attrib = ''
        self.packet = {}

    def getItemName(self):
        return self.item_name

    def getItemId(self):
        return self.item_id

    def getItemLen(self):
        return self.item_len

    def setPkt(self, pkt_type, pkt):
        self.packet[pkt_type] = pkt

    def getPkt(self):
        return self.packet

    def setIndex(self, flag):
        if flag:
            self.attrib += 'I'
        else:
            self.attrib = self.attrib.replace('I', '')

    def setCreate(self, flag):
        if flag:
            self.attrib += 'C'
        else:
            self.attrib = self.attrib.replace('C', '')

    def setModify(self, flag):
        if flag:
            self.attrib += 'M'
        else:
            self.attrib = self.attrib.replace('M', '')

    def setRead(self, flag):
        if flag:
            self.attrib += 'R'
        else:
            self.attrib = self.attrib.replace('R', '')

    def setAttr(self, idx, modify, create, read):
        if not idx == '0':
            self.setIndex(True)

        if modify == '1':
            self.setModify(True)

        if create == '1':
            self.setCreate(True)

        if read == '1':
            self.setRead(True)

        return self.attrib

    def getAttr(self):
        return self.attrib

    def setCombineId(self, combine_id):
        self.attrib = self.attrib.replace('M', '')
        self.combine_id = combine_id

def genLen(pkt):
    if type(pkt) == int:
        length = pkt
    elif type(pkt) == str:
        pkt = pkt.replace('.', '')
        var_len = 0
        while '[' in pkt and ']' in pkt:
            start = pkt.find('[')
            end = pkt.find(']')
            var_data = pkt[start + 1:end]
            if '|' in var_data:
                var_len += int(var_data[var_data.find('|') + 1:])
            else:
                var_len += len(var_data)

            pkt = pkt[:start] + pkt[end + 1:]

        length = len(pkt) / 2 + var_len

    if length < 0x80:
        return '%02x' % length
    elif length < 0x4000:
        return '%04x' % (length + 0x8000)
    elif length < 0x200000:
        return '%06x' % (length + 0xc00000)
    elif length < 0x10000000:
        return '%08x' % (length + 0xe0000000)

def genObjIdx(tbl_id, index_list, flag):
    obj_idx = ''
    if len(index_list) == 0:
        obj_idx = '0x70.%s.%s' % (genLen(PHYSICALID), PHYSICALID)
    else:
        for item in index_list:
            obj_type = 0
            if item == index_list[-1]:
                obj_type |= 1 << 4

            if flag == 'Dynamic':
                obj_type |= 1 << 5

            pkt_temp = '%s%s.[%s|%d]' % (tbl_id, item.getItemId(), item.getItemName(), item.getItemLen())
            obj_idx += '.%02x.%s.%s' % (obj_type, genLen(pkt_temp), pkt_temp)

        obj_idx = '00.08.0100101001.000000' + obj_idx
        obj_idx = '0x70.%s.%s' % (genLen(obj_idx), obj_idx)

    return obj_idx


def genFunIdx(tbl_id, item_id, flag):
    fun_idx = '%s%s' % (tbl_id, item_id)
    fun_idx = '10.%s.%s' % (genLen(pkt=fun_idx), fun_idx)
    if flag == 'set':
        fun_idx = '0x10.%s.%s' % (genLen(fun_idx), fun_idx)
    elif flag == 'create':
        fun_idx = '0x11.%s.%s' % (genLen(fun_idx), fun_idx)
    elif flag == 'get':
        fun_idx = '0x30.%s.%s' % (genLen(fun_idx), fun_idx)
    else:
        fun_idx = ''

    return fun_idx


def genPayload(tbl_id, item_list, flag):
    payload = ''
    has_string = False
    for item in item_list:
        if flag == 'set':
            if item.item_type == 'DISPLAYSTRING' or item.item_type == 'OCTSTRING':
                var_data = '[%s]' % item.getItemName()
                payload += '.%s[%s].%s' % (item.getItemId(), genLen(var_data), var_data)
                has_string = True
            else:
                var_data = '[%s|%d]' % (item.getItemName(), item.getItemLen())
                payload += '.%s%s.%s' % (item.getItemId(), genLen(var_data), var_data)
        elif flag == 'get':
            payload += '.%s.%s' % (item.getItemId(), genLen(0))
        else:
            return ''

    if has_string:
        payload = '%s.[%s]%s' % (tbl_id, genLen(payload), payload)
        payload = '0x60.[%s].%s' % (genLen(payload), payload)
    else:
        payload = '%s.%s%s' % (tbl_id, genLen(payload), payload)
        payload = '0x60.%s.%s' % (genLen(payload), payload)

    return payload
