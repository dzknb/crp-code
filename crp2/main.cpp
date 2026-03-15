#include<iostream>
#include<fstream>
#include<cstdint>
#include<stack>
#include<cstring>

#pragma pack(push,1)
#define MAXINDEX 16
#define BYTE 16

struct int40 //code段单体结构
{
    uint8_t CMD;
    uint16_t R1;
    uint16_t R2;
};
int40 data[MAXINDEX] = {}; //code段
uint16_t value[MAXINDEX] = {}; //data段

std::stack<uint16_t> got_label; //跳转地址盏

int run()
{
    value[0] = 0b1000000000000000; //状态储存地址 
    /*状态对应信息 
        [0]运行模式     0:特殊      1:正常             
        [1]
    */
    uint16_t run_idx = 0,exc_R1 = 0,exc_R2 = 0;
    while(run_idx < MAXINDEX)   
    {
        uint16_t R1 = data[run_idx].R1 + exc_R1;
        uint16_t R2 = data[run_idx].R2 + exc_R2;

        
        //std::printf("%02X %04X %04X\n", data[run_idx].CMD, data[run_idx].R1, data[run_idx].R2);
        switch (data[run_idx].CMD)
        {
        case 0x00://nop
            break;
        case 0x01://mov [R1] [R2]
            value[R1] = value[R2];
            break;

        case 0x02://mov [R1] R2
            value[R1] = R2;
            break;

        case 0x03://got
            if(R2 != 0xFFFF)
            {
                got_label.push(run_idx);
            }
            run_idx = R1 - 1; 
            break;
        
        case 0x04://got 返回上一个记录的跳转点
            run_idx = got_label.top();
            got_label.pop();
            break;

        case 0x05://cmp [R1] [R2]
            if(value[R1] != value[R2])
            {
                run_idx += 1;
            }
            break;

        case 0x06://cmp [R1] R2
            if(value[R1] != R2)
            {
                run_idx += 1;
            }
            break;


        case 0x07://add [R1] [R2]
            value[R1] = value[R1] + value[R2];
            break;

        case 0x08://add [R1] R2
            value[R1] = value[R1] + R2;
            break;
        

        case 0x09://and [R1] [R2]
            value[R1] = value[R1] & value[R2];
            break;
        
        case 0x10://and [R1] R2
            value[R1] = value[R1] & R2;
            break;
        

        case 0x11://orx [R1] [R2]
            value[R1] = value[R1] | value[R2];
            break;

        case 0x12://orx [R1] R2
            value[R1] = value[R1] | R2;
            break;

        
        case 0x13://xor [R1] [R2]
            value[R1] = value[R1] ^ value[R2];
            break;

        case 0x14://xor [R1] R2
            value[R1] = value[R1] ^ R2;
            break;


        case 0x15://not [R1] [R2]
            value[R1] = ~value[R2];
            break;
        
        case 0x16://not [R1] R2
            value[R1] = ~R2;
            break;

        //cal 0x17 0x18


        case 0x19://exc [R1] [R2]
            exc_R1 = value[data[run_idx].R1]; //不受上一个偏移影响
            exc_R2 = value[data[run_idx].R2];
            break;

        case 0x20://exc R1 R2
            exc_R1 = data[run_idx].R1; //不受上一个偏移影响
            exc_R2 = data[run_idx].R2;
            break;


        case 0x21://shl [R1] [R2]
            value[R1] = value[R1] << value[R2];
            break;

        case 0x22://shl [R1] R2
            value[R1] = value[R1] << R2;
            break;

        case 0x23://shr [R1] [R2]
            value[R1] = value[R1] >> value[R2];
            break;

        case 0x24://shr [R1] R2
            value[R1] = value[R1] >> R2;
            break;

        case 0xFF://deb
            if(R2 == 0x0000)//输出内存
            {
                std::cout<<value[R1]<<std::endl;
            }
            break;

        default:
            break;
        }
        run_idx += 1;
    }
    return 0;
}


int main()
{
    
    char head[5] = {}; //'crp1 ' <- 文件头

    std::ifstream file("example.bin",std::ios::binary|std::ios::ate);
    if(!file.is_open())
    {
        std::cout<<"文件打开失败"<<std::endl;
    }
    file.seekg(0); // 回到开头
   
    file.read(reinterpret_cast<char*>(head),(std::streamsize(sizeof(char)) * 5)); //读取文件头

    file.read(reinterpret_cast<char*>(data),(std::streamsize(sizeof(int40)) * MAXINDEX)); //读取code段

    file.read(reinterpret_cast<char*>(value),(std::streamsize(sizeof(uint16_t)) * MAXINDEX)); //读取data段
    
    if(strcmp(head,"crp1 ") == 0)//检查文件头
    {
        std::cout<<"开始执行\n"<<std::endl;
        run();
        std::cout<<"结束执行\n"<<std::endl;
    }
    else
    {
        std::cout<<"文件头错误"<<std::endl;
    }

    return 0;
}
