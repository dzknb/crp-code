import struct

#常量定义
MAXINDEX = 16
BYTES = 16

#代码编写区↓
code =\
"""
int [0x0001] 0xFFFF
deb [0x0001]
""".split('\n')

code_data = [[0x00,0x0000,0x0000] for i in range(MAXINDEX)] #[[CMD,ARGU1,ARGU2],[CMD,ARGU1,ARGU2],...]
value_data = [0x0000 for i in range(MAXINDEX)] #[value,value,...]

variable = {} #变量表 name -> value
label = {} #标签表 name -> address

def error(message): #报错调用，后期修改
    print(message)
    exit(0)

def return_type(data): #返回 值 的类型
    data = str(data)

    data_head = data[0]
    data_end = data[-1]

    if data_head == '[' and data_end == ']':
        return 'ADDRESS'
    
    elif data_head == "'" and data_end == "'":
        return 'CHAR'
    
    elif data_head == '_':
        return 'VARIABLE'
    
    elif data_head == '~':
        return 'LABEL'
    
    else:
        return 'INT'
    
def check_variable(name): #在正式处理阶段使用
    if name in variable.keys():
        return True
    
    else:
        return False

def return_address(name): #在正式处理阶段使用
    if check_variable(name):
        return int(variable[name])
    
    else:
        return False
    
def crp_char(data): #字符 -> 字符码（16位）
    #这里是查表返回，未完成（返回int）
    return 0 #此处返回字符码

def int_addr(address): #[0xXXXX] -> 0xXXXX 
    return int(str(address)[1:-1],0)

def idx_bool(argu,idx): #返回指定操作数的值（布尔），如果是"true",返回ture;不存在或不是“true”时返回false
    try:
        argu[int(idx)]

    except:
        return False
    
    else:
        if argu[int(idx)] == 'true':
            return True


#预处理:空白，标签，注释 替换变量，new（声明变量，代替地址），imp（导入包），mem（获取变量实际地址），int（向data区写如初始数据），def（宏替换）
pro_code = []
variable_addr = {} #储存变量地址 name -> address
variable_addr_count = 0x0001 #变量从[0x0001]开始存储，[0x0000]存储设定
def_data = {} #储存宏定义 new_name -> value

#此处处理imp，未完成功能

for line in code: #处理：new 空白 注释 def识别
    if str(line).isspace() or line == '': #判断是否为空白行
        continue

    elif str(line)[0] == ';': #判断注释
        continue
    
    cmd = line.split(' ')[0]
    try: #防止无参数情况
        argu = line.split(' ')[1:]

    except:
        argu = ['','']

    if cmd == 'new': #声明变量，代替地址
        for new_variable in argu: #new _VARIABLE1 _VARIABLE2 ... _VARIABLE
            if return_type(new_variable) == 'VARIABLE':
                if new_variable in variable_addr.keys():
                    error('new variable exist')
                
                else:
                    variable[new_variable] = 0x0000
                    variable_addr[new_variable] = variable_addr_count
                    variable_addr_count += BYTES #累加分配的地址

            else:
                error('new argu not variable')
        
        continue #不加入new行

    elif cmd == 'def': #宏替换 注意:此处识别替换字符时因考虑 “xxx xxx” 等字符串中包含空格的情况，未来需修改
        def_data[argu[1]] = argu[0]
        continue #不加入def行

    else:
        pro_code.append(line) #保留有效代码

#处理宏替换
#未完成

pro_code_second = []
run_idx_for_label =  0 #标签记录函数，需要单独累加，避免编译优化导致行数错误
for line_number in range(len(pro_code)): #处理：mem 标签 int
    line = pro_code[line_number]
    cmd = line.split(' ')[0]

    try: #防止无参数情况
        argu = line.split(' ')[1:]

    except:
        argu = ['','']

    if line[0] == '~': #标签
        label[str(line.split(' ')[0])] = int(run_idx_for_label) - 1
        continue 

    elif cmd == 'mem': #获取 _variable 的地址
        if return_type(argu[0]) == 'VARIABLE': #mem _ADDRESS _VARIABLE -> _ADDRESS = [_VARIABLE]
            if argu[0] in variable_addr.keys() and argu[1] in variable_addr.keys():
                variable[argu[0]] = variable_addr[argu[1]] #间接向variable写入
                continue

            else:
                error('mem variable not exist')

        else:
            error('mem argu not variable')

    elif cmd == 'int': #直接线data区写入初始数据
        if return_type(argu[1]) == 'CHAR': #此处还未进行预处理，需要单独区分char
            argu[1] = crp_char(argu[1]) #直接替换argu[1]

        if argu[0] in variable_addr.keys(): #int _VARIABLE VALUE
            value_data[variable_addr[argu[0]]] = int(argu[1],0) #直接向value_data写入
            variable[argu[0]] = int(argu[1],0)
            continue

        elif return_type(argu[0]) == 'ADDRESS':
            value_data[int_addr(argu[0])] = int(argu[1],0) #直接向value_data写入
            continue

        else:
            error('int argu1 can not write')
        

    pro_code_second.append(line)
    run_idx_for_label += 1 #空白和注释行在上一阶段被移除，mem和标签行不计入行数

pro_code = pro_code_second
code = []

for line in pro_code: #处理：替换变量      注意：不能替换标签，因为跳转只能依靠标签标签
    new_line = str(line.split(' ')[0] + ' ') #新生成的行（处理过）
    try: #防止无参数情况
        argu = line.split(' ')[1:]

    except:
        argu = ['','']

    for i in argu: #遍历每行参数，替换数据
        if return_type(i) == 'VARIABLE': 
            if i in variable_addr.keys():
                new_line = new_line + '[' + str(variable_addr[i]) + '] '

            else:
                error('pro-code:"' + str(i) + '" variable not exist')

        elif return_type(i) == 'CHAR': #处理字符
            new_line = new_line + crp_char(i) + ' '

        else:
            new_line = new_line + i + ' '

    code.append(new_line)


#正式处理
run_idx = 0
for line in code:
    command = line.split(' ')[0]
    try: #防止无参数情况
        argu = line.split(' ')[1:]

    except:
        argu = ['','']

    if command == 'nop': #nop - -   -> 0x00 0000 0000
        code_data[run_idx] = [0x00,0x0000,0x0000]

    elif command == 'mov': #0x01 0x02
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x01,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x02,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('mov argu1 not address')


    elif command == 'got': #0x03 0x04
        if return_type(argu[0]) == 'LABEL':
            if argu[0] == '~': #返回 
                code_data[run_idx] = [0x04,0x0000,0x0000]
            else:
                if argu[0] in label.keys():
                    if idx_bool(argu,1):
                        code_data[run_idx] = [0x03,label[argu[0]],0x0000]
                    
                    else: #静默跳转
                        code_data[run_idx] = [0x03,label[argu[0]],0xFFFF]
        else:
            error('got argu1 not label')


    elif command == 'cmp': #0x05 0x06
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x05,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x06,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('cmp argu1 not address')


    elif command == 'add': #0x07 0x08
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x07,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x08,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('add argu1 not address')


    elif command == 'and': #0x09 0x10
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x09,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x10,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('and argu1 not address')
  

    elif command == 'orx': #0x11 0x12
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x11,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x12,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('orx argu1 not address')


    elif command == 'xor': #0x13 0x14
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x13,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x14,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('xor argu1 not address')


    elif command == 'not': #0x15 0x16
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x15,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x16,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('not argu1 not address')


    #cal未完成 0x17 0x18


    elif command == 'exc': #0x19 0x20
        if return_type(argu[0]) != return_type(argu[1]):
            error('exc argu type not same')

        else:
            if return_type(argu[0]) == 'ADDRESS':
                code_data[run_idx] = [0x19,int_addr(argu[0]),int_addr(argu[1])]
                
            else: #R1，R2是立即数
                code_data[run_idx] = [0x20,int(argu[0],0),int(argu[1],0)]


    elif command == 'shl': #0x21 0x22
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x21,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x22,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('shl argu1 not address')


    elif command == 'shr': #0x23 0x24
        if return_type(argu[0]) == 'ADDRESS':
            if return_type(argu[1]) == 'ADDRESS': #R1 是 变量（地址）
                code_data[run_idx] = [0x23,int_addr(argu[0]),int_addr(argu[1])]
            
            else: #R2是立即数
                code_data[run_idx] = [0x24,int_addr(argu[0]),int(argu[1],0)]

        else:
            error('shr argu1 not address')


    elif command == 'deb': #0xFF 调试指令，输出 [R1] 的值
        code_data[run_idx] = [0xFF,int_addr(argu[0]),0x0000]


    else: #无法识别的命令
        error('unkown command')

    run_idx += 1


#处理写入数据
for variable_name,variable_address in variable_addr.items():
    value_data[variable_address] = variable[variable_name]


#生成文件
with open('./example.bin','wb') as file: 
    print('CODE:')
    
    file.write(b'crp1 ') #文件头

    for line in code_data: #code区
        write_data = struct.pack('< B H H',line[0],line[1],line[2])
        print(write_data)
        file.write(write_data)

    print('DATA:')
    for line in value_data: #data区
        write_data = struct.pack('< H',line)
        file.write(write_data)
        print(write_data)

"""
    [_A] 和 _A 的区别
    
    假设：_A -> 0x0001，[0x0001] -> 9

    mov _A 1     ->   将 1 赋值到 [0x0001]  =  mov [0x0001] 1

    mov [_A] 1   没有这种写法

"""
