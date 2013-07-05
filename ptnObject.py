'''
Created on 2013-7-3

@author: dlash
'''

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
                self.combine_list.add(item.combine_id)
                if combine_item.has_key(item.combine_id):
                    combine_item[item.combine_id].append(item)
                else:
                    combine_item[item.combine_id] = [item]


        self.pkt['obj_idx'] = genObjIdx(self.tbl_id, index_list, self.tbl_type)
        self.pkt['create.fun_idx'] = genFunIdx(self.tbl_id, 'FF', 'create')
        self.pkt['create.payload'] = genPayload(self.tbl_id, create_list, 'set')
        self.pkt['get.fun_idx'] = genFunIdx(self.tbl_id, 'FF', 'get')
        self.pkt['get.payload'] = genPayload(self.tbl_id, get_list, 'get')
        
        for comb in self.combine_list:
            self.pkt['%s.fun_idx' % comb] = genFunIdx(self.tbl_id, comb, 'set')
            self.pkt['%s.payload' % comb] = genPayload(self.tbl_id, combine_item[comb], 'set')

class ptn_item(object):
    '''
    classdocs
    '''

    def __init__(self, name, item_id, item_len):
        self.item_name = name
        self.item_id = item_id
        self.item_len = int(item_len)
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


def genLen_Index(pkt):
    if type(pkt) == int:
        length = pkt
    elif type(pkt) == str:
        pkt = pkt.replace('.', '').replace('[', '').replace(']', '')
        length = len(pkt) / 2

    if length < 0x80:
        return '%02x' % length
    elif length < 0x4000:
        return '%04x' % (length + 0x8000)
    elif length < 0x200000:
        return '%06x' % (length + 0xc00000)
    elif length < 0x10000000:
        return '%08x' % (length + 0xe0000000)


def genLen_Payload(pkt):
    if type(pkt) == int:
        length = pkt
    elif type(pkt) == str:
        pkt = pkt.replace('.', '').replace('[', '').replace(']', '')
        length = len(pkt) / 2

    return '%04x' % (length + 0x8000)

PHYSICALID = '0x70.0a.10.08.0100101001.000000'
def genObjIdx(tbl_id, index_list, flag):
    obj_idx = ''
    length = 0
    for item in index_list:
        if item == index_list[-1]:
            obj_type = '10'
            if flag == 'Dynamic':
                obj_type = '30'
            obj_idx += '%s.%s.%s%s.%s' % (obj_type, genLen_Index(item.getItemLen() + 5), tbl_id, item.getItemId(), item.getItemName())
        else:
            obj_type = '00'
            if flag == 'Dynamic':
                obj_type = '20'
            obj_idx += '%s.%s.%s%s.%s.' % (obj_type, genLen_Index(item.getItemLen() + 5), tbl_id, item.getItemId(), item.getItemName())
        length += item.getItemLen() + 5 + len(genLen_Index(item.getItemLen() + 5)) / 2 + 1

    if length == 0:
        obj_idx = PHYSICALID
    else:
        obj_idx = '0x70.%s.00.08.0100101001.000000.%s' % (genLen_Index(length + 10), obj_idx)

    return obj_idx


def genFunIdx(tbl_id, item_id, flag):
    fun_idx = '%s%s' % (tbl_id, item_id)
    fun_idx = '10.%s.%s' % (genLen_Index(pkt=fun_idx), fun_idx)
    if flag == 'set':
        fun_idx = '0x10.%s.%s' % (genLen_Index(pkt=fun_idx), fun_idx)
    elif flag == 'create':
        fun_idx = '0x11.%s.%s' % (genLen_Index(pkt=fun_idx), fun_idx)
    elif flag == 'get':
        fun_idx = '0x30.%s.%s' % (genLen_Index(pkt=fun_idx), fun_idx)
    else:
        fun_idx = ''

    return fun_idx


ITEM_ID_LEN = 1
TABLE_ID_LEN = 4
PAYLOAD_LENGTH_LEN = 2
def genPayload(tbl_id, item_list, flag):
    payload = ''
    length = 0
    for item in item_list:
        if flag == 'set':
            payload += '.%s%s.%s' % (item.getItemId(), genLen_Payload(item.getItemLen()), item.getItemName())
            length += ITEM_ID_LEN + PAYLOAD_LENGTH_LEN + item.getItemLen()
        elif flag == 'get':
            payload += '.%s.%s' % (item.getItemId(), genLen_Payload(0))
            length += ITEM_ID_LEN + PAYLOAD_LENGTH_LEN
        else:
            return ''
    payload = '%s.%s%s' % (tbl_id, genLen_Payload(length), payload)
    length += TABLE_ID_LEN + PAYLOAD_LENGTH_LEN
    payload = '0x60.%s.%s' % (genLen_Index(length), payload)

    return payload
