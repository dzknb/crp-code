import struct

MAXIDX = 16

def return_type(data):
    data_head = str(data)[0]
    data_end = str(data)[-1]
    if data_head == '_':
        return 'VALUE'
    
    elif data_head == '~':
        return 'LABEL'
    
    else:
        return 'INT'

def value_split(data): #_A:1
    value_name = data.split(':')[0]
    value_exc = 1
    if ':' in str(data):
        value_exc = int(str(data).split(':')[1],0)
    return [value_name,value_exc]

def error(message):
    print(message,'\n',line)
    exit()

code =\
"""
new _a
~loop
deb _a
add _a 1
cmp _a 99
got ~end
got ~loop
~end
"""

code = code.split('\n')

code_data = [[0,0,0] for i in range(MAXIDX)]
value_data = [0 for i in range(MAXIDX)] #idx -> 数据
label_data = [0 for i in range(MAXIDX)] #idx -> 数据

value = {} #name -> 地址
label = {} #name -> 地址

value_idx = 0
label_idx = 0
code_idx = 0


run_idx = -1
while run_idx < len(code) - 1: #预处理
    run_idx += 1

    line = code[run_idx]
    command = line.split(' ')[0]

    if line == '':
        continue
    elif line[0] == ';':
        continue
    
    if command == 'imp':
        with open(('./pack/' + line.split(' ')[1] + '.crp'),'r',encoding='utf-8') as file:
            for file_line in file.readlines():
                code.append(file_line.rstrip())

    elif command in ['mov','got','cmp','add','deb','cal','exc','shl','shr']:
        code_idx += 1
        continue

    elif line[0] == '~': #Label
        if line in label.keys():
            label_data[label_idx] = code_idx
        else:
            label[line] = label_idx
            label_data[label_idx] = code_idx
            label_idx += 1

    elif command == 'new':
        for create_value in line.split(' ')[1:]:
            if return_type(create_value) == 'VALUE':
                create_value_data = value_split(create_value)
                if create_value_data[0] in value.keys():
                    error('new exist')
                else:
                    value[create_value_data[0]] = value_idx
                    value_data[value_idx] = 0
                    value_idx += create_value_data[1]
            else:
                error('new not value')

code_idx = 0

for line in code:
    if line == '':
        continue
    elif line[0] == ';':
        continue

    command = line.split(' ')[0]
    argu = line.split(' ')[1:]
    
    if command == 'mov': #0x01
        if return_type(argu[1]) == 'INT':    
            value_data[value_idx] = int(argu[1],0)
            opera_idx = value_idx
            value_idx += 1
            
            
            '''
            if return_type(argu[0]) == 'VALUE':

                value_data[value[argu[0]]] = int(argu[1],0)
            else:
                error('mov not value')

            '''

        
        elif argu[1] in value.keys():
            opera_idx = value[argu[1]]
        else:
            error('mov value2 not exist')

        if return_type(argu[0]) == 'VALUE':
                
            if argu[0] in value.keys():
                code_data[code_idx] = ([0x01,value[argu[0]],opera_idx])
                code_idx += 1

            else:
                error('mov value1 not exist')
        else:
            error('mov not value')

    elif command == 'got': #0x02
        if return_type(argu[0]) == 'LABEL':
            if argu[0] == '~':
                code_data[code_idx] = [0x02,0xFFFF,0xFFFF]
            elif len(argu) == 2 and argu[1] == 'False':
                code_data[code_idx] = [0x02,label[argu[0]],0xFFFF]    
            else:
                code_data[code_idx] = [0x02,label[argu[0]],0x0000]

            
            code_idx += 1

        else:
            error('got not label')

    elif command == 'cmp': #0x03
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera_idx = value[argu[1]]
            else:
                error('cmp value2 not exist')
        
        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx]=[0x03,value[argu[0]],opera_idx]
                code_idx += 1
            else:
                error('cmp value1 not exist')
        else:
            error('cmp not value')

    elif command == 'add': #0x04
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera_idx = value[argu[1]]
            else:
                error('add value2 not exist')
        
        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx] = [0x04,value[argu[0]],opera_idx]
                code_idx += 1

            else:
                error('add value1 not exist')
        else:
            error('add not value')

    elif command == 'and': #0x05
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera_idx = value[argu[1]]
            else:
                error('and value2 not exist')
        
        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx] = [0x05,value[argu[0]],opera_idx]
                code_idx += 1

            else:
                error('and value1 not exist')
        else:
            error('and not value')

    elif command == 'orx': #0x06
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera_idx = value[argu[1]]
            else:
                error('orx value2 not exist')
        
        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx] = [0x06,value[argu[0]],opera_idx]
                code_idx += 1

            else:
                error('orx value1 not exist')
        else:
            error('orx not value')
        
    elif command == 'xor': #0x07
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera_idx = value[argu[1]]
            else:
                error('xor value2 not exist')
        
        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx] = [0x07,value[argu[0]],opera_idx]
                code_idx += 1

            else:
                error('xor value1 not exist')
        else:
            error('xor not value')

    elif command == 'not': #0x08

        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx] = [0x08,value[argu[0]],0x0000]
                code_idx += 1

            else:
                error('not value not exist')
        else:
            error('not not value')
    
    elif command == 'cal': #0x09
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera2_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera2_idx = value[argu[1]]
            else:
                error('cal value2 not exist')

        if return_type(argu[0]) == 'INT':
            value_data[value_idx] = int(argu[0],0)
            opera1_idx = value_idx
            value_idx += 1
        else:
            if argu[0] in value.keys():
                opera1_idx = value[argu[0]]
            else:
                error('cal value2 not exist')
        
        code_data[code_idx] = [0x09,opera1_idx,opera2_idx]
        code_idx += 1

    elif command == 'exc': #0x0a
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera2_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera2_idx = value[argu[1]]
            else:
                error('exc value2 not exist')

        if return_type(argu[0]) == 'INT':
            value_data[value_idx] = int(argu[0],0)
            opera1_idx = value_idx
            value_idx += 1
        else:
            if argu[0] in value.keys():
                opera1_idx = value[argu[0]]
            else:
                error('exc value2 not exist')
        
        code_data[code_idx] = [0x0a,opera1_idx,opera2_idx]
        code_idx += 1

    elif command == 'shl': #0x0b
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera2_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera2_idx = value[argu[1]]
            else:
                error('shl value2 not exist')

        if return_type(argu[0]) == 'INT':
            value_data[value_idx] = int(argu[0],0)
            opera1_idx = value_idx
            value_idx += 1
        else:
            if argu[0] in value.keys():
                opera1_idx = value[argu[0]]
            else:
                error('shl value2 not exist')
        
        code_data[code_idx] = [0x0b,opera1_idx,opera2_idx]
        code_idx += 1

    elif command == 'shr': #0x0c
        if return_type(argu[1]) == 'INT':
            value_data[value_idx] = int(argu[1],0)
            opera2_idx = value_idx
            value_idx += 1
        else:
            if argu[1] in value.keys():
                opera2_idx = value[argu[1]]
            else:
                error('shr value2 not exist')

        if return_type(argu[0]) == 'INT':
            value_data[value_idx] = int(argu[0],0)
            opera1_idx = value_idx
            value_idx += 1
        else:
            if argu[0] in value.keys():
                opera1_idx = value[argu[0]]
            else:
                error('shr value2 not exist')
        
        code_data[code_idx] = [0x0c,opera1_idx,opera2_idx]
        code_idx += 1

    elif command == 'deb': #0xff
        if return_type(argu[0]) == 'VALUE':
            
            if argu[0] in value.keys():
                code_data[code_idx]= [0xff,value[argu[0]],0x00]
                code_idx += 1
            else:
                error('deb value1 not exist')
        else:
            error('deb not value')


with open('./example.bin','wb') as file:
    print('CODE:')
    for line in code_data:
        write_data = struct.pack('< B H H',line[0],line[1],line[2])
        print(write_data)
        file.write(write_data)

    print('DATA:')
    for line in value_data:
        write_data = struct.pack('< H',line)
        file.write(write_data)
        print(write_data)

    print("LABEL:")
    for line in label_data:
        write_data = struct.pack('< H',line)
        print(write_data)
        file.write(write_data)