from xml.etree import ElementTree as et
import copy

def partDividedBody(tree, part_id, part_name, score_name):
    tree_divided = copy.deepcopy(tree)
    root = tree_divided.getroot()
    part_list = root.find('part-list')
    score_part = part_list.findall('score-part')
    for i in range(len(score_part)):
        if part_id != score_part[i].attrib['id']:
            part_list.remove(score_part[i])
    parts = root.findall('part')
    for i in range(len(parts)):
        if part_id != parts[i].attrib['id']:
            root.remove(parts[i])
    tree_divided.write(part_name+"_"+score_name, encoding='UTF-8', xml_declaration=True)

def partDivided(score_name):
    tree = et.parse(score_name)
    root = tree.getroot()
    part_list = root.find('part-list')
    score_part = part_list.findall('score-part')
    part_id_list = []
    part_name_list = []
    for i in range(len(score_part)):
        part_id_list.append(score_part[i].attrib['id'])
        part_name_list.append(score_part[i].findtext('part-name'))
    
    print(part_id_list)
    print(part_name_list)

    for i in range (len(part_id_list)):
        partDividedBody(tree, part_id_list[i], part_name_list[i], score_name)

    '''
    parts = root.findall('part')
    
    for i in range(len(parts)):
        print(part_id_list.index(parts[i].attrib['id']))
    '''

score_name = 'nippon.musicxml'
partDivided(score_name)