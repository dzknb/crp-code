#include<iostream>
#include<fstream>
#include<cstdint>
#include<stack>

#pragma pack(push,1)
#define MAXINDEX 16
#define BYTE 16

struct int40
{
    uint8_t CMD;
    uint16_t R1;
    uint16_t R2;
};
int40 data[MAXINDEX] = {}; //code段
uint16_t value[MAXINDEX] = {}; //data段
uint16_t label[(MAXINDEX)] = {}; //label段

std::stack<uint16_t> got_label;

#include "./devices/FF.cpp" //导入设备

int print()
{
    for(uint16_t i=0;i<MAXINDEX;i++)
    {
        std::printf("%02X %04X %04X\n", data[i].CMD, data[i].R1, data[i].R2);
    }
    std::cout<<"DATA:"<<std::endl;
    for(uint16_t i=0;i<MAXINDEX;i++)
    {
        std::printf("%04X\n", value[i]);
    }
    std::cout<<"LABEL:"<<std::endl;
    for(uint16_t i=0;i<MAXINDEX;i++)
    {
        std::printf("%04X\n", label[i]);
    }
    std::cout<<"开始执行"<<std::endl;
    return 0;
}

int run()
{
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
        case 0x01://mov
            value[R1] = value[R2];
            break;
        case 0x02://got
            if(R1 == 0xFFFF)
            {
                run_idx = got_label.top();
                //std::printf("%d",run_idx);
                got_label.pop();
                break;
            }
            else if(R2 != 0xFFFF)
            {
                got_label.push(run_idx);
            }
            run_idx = label[R1] - 1; 
            break;

        case 0x03://cmp
            if(value[R1] != value[R2])
            {
                run_idx += 1;
            }
            break;
            
        case 0x04://add
            value[R1] = value[R1] + value[R2];
            break;
        
        case 0x05://and
            value[R1] = value[R1] & value[R2];
            break;
        
        case 0x06://orx
            value[R1] = value[R1] | value[R2];
            break;
        
        case 0x07://xor
            value[R1] = value[R1] ^ value[R2];
            break;

        case 0x08://not
            value[R1] = ~value[R1];
            break;
        
        case 0x09://cal
            _FF::cal(value[R1]>>8,value[R1]&0xFF,R2); //固定设备调用
            break; 

        case 0x0a://exc
            exc_R1 = value[data[run_idx].R1]; //不受上一个偏移影响
            exc_R2 = value[data[run_idx].R2];
            break;

        case 0x0b://shl
            value[R1] = value[R1] << value[R2];
            break;

        case 0x0c://shr
            value[R1] = value[R1] >> value[R2];
            break;

        case 0xFF://deb
            std::cout<<value[R1]<<std::endl;
            break;

        default:
            break;
        }
        run_idx += 1;

        _FF::cal(0xFF,0xFF,0X0000);//tick触发
    }
    return 0;
}

int main()
{
 

    std::ifstream file("example.bin",std::ios::binary|std::ios::ate);
    if(!file.is_open())
    {
        std::cout<<"Error,Can't open file"<<std::endl;
    }
    file.seekg(0); // 回到开头
   
    file.read(reinterpret_cast<char*>(data),(std::streamsize(sizeof(int40)) * MAXINDEX));

    file.read(reinterpret_cast<char*>(value),(std::streamsize(sizeof(uint16_t)) * MAXINDEX));
    
    file.read(reinterpret_cast<char*>(label),(std::streamsize(sizeof(uint16_t)) * MAXINDEX));

    print();
    run();

    return 0;
}
