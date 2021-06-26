from xml.etree import ElementTree as et
import copy
import numpy as np

def getChordNumInfo(measures):
    chord_info = []
    for i in range(len(measures)):
        chord_info.append([])
        notes = measures[i].findall('note')
        chord_num = 1
        for j in range(len(notes)):
            if notes[j].find('chord') == None:
                chord_num = 1
            else:
                chord_num += 1
            chord_info[i].append(chord_num)
    return chord_info

def listMulti(list_a, list_b):
    return (np.array(list_a) * np.array(list_b)).tolist()

def listAdd(list_a, list_b):
    return (np.array(list_a) + np.array(list_b)).tolist()

def getChordGroup(measure_chord_info):
    chord_group = np.where(np.array(measure_chord_info) == 1)[0].tolist()
    chord_group.append(len(measure_chord_info))
    return chord_group

def chordDivisionDivideBody(tree, chord_info, part_num):
    tree_divided = copy.deepcopy(tree)
    root = tree_divided.getroot()
    part = root.find('part')
    measures = part.findall('measure')
    for i in range(len(chord_info)): #小節ごと [1,1,2,1,2,3]
        select_note_total = [0] * len(chord_info[i])
        chord_group = getChordGroup(chord_info[i]) # [0,1,3,6]chord groupの始点インデックス
        for j in range(len(chord_group)): # chord groupごとにどの音を選ぶか選択する
            if chord_group[j] == len(chord_info[i]):
                break
            note_ind = range(len(chord_info[i])) # [0,1,2,3,4,5]
            note_mask = [(el>=chord_group[j]) and (el<chord_group[j+1]) for el in note_ind] # j=0: [1,0,0,0,0,0], j=1: [0,1,1,0,0,0], j=2: [0,0,0,1,1,1]
            target_note = listMulti(chord_info[i],note_mask) # j=1: [0,1,2,0,0,0], j=2: [0,0,0,1,2,3]
            target_note = np.where(np.array(target_note) > part_num, 0, np.array(target_note)).tolist() # part_numよりおおきいものは削除 j=1,part_num=1: [0,1,0,0,0,0], j=2,part_num=2: [0,0,0,1,2,0]
            select_note_mask = [0] * len(chord_info[i])
            select_note_mask[target_note.index(max(target_note))] = 1 #j=2,part_num=2: [0,0,0,0,1,0] part_num以下で最大の値を取ってくる
            select_note = listMulti(chord_info[i], select_note_mask)
            select_note_total = listAdd(select_note_total,select_note) # part_num=2: [1,0,2,0,2,0]
        notes = measures[i].findall('note')
        for k in range(len(chord_info[i])):
            if notes[k].find("chord") != None:
                notes[k].remove(notes[k].find("chord"))
            if select_note_total[k] != 0:
                continue
            else:
                measures[i].remove(notes[k])
    return tree_divided

def chordDivisionDivide(tree):
    root = tree.getroot()
    part = root.find('part')
    measures = part.findall('measure')
    chord_info = getChordNumInfo(measures)
    tree_divided_chord = []
    max_chord_num = max(sum(chord_info, []))
    for i in range(max_chord_num):
        tree_divided_chord.append(chordDivisionDivideBody(tree, chord_info, i+1))
    return tree_divided_chord

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
    tree_divided_chord = chordDivisionDivide(tree_divided)
    for i in range(len(tree_divided_chord)):
        tree_divided_chord[i].write(part_name+"_chord"+str(i+1)+"_"+score_name, encoding='UTF-8', xml_declaration=True)

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
    
    print("構成パートID: {}".format(part_id_list))
    print("構成パート名: {}".format(part_name_list))

    for i in range (len(part_id_list)):
        partDividedBody(tree, part_id_list[i], part_name_list[i], score_name)

    '''
    parts = root.findall('part')
    
    for i in range(len(parts)):
        print(part_id_list.index(parts[i].attrib['id']))
    '''

score_name = 'nippon.musicxml'
partDivided(score_name)