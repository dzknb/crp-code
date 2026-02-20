#include <iostream>
#include <cstdint>
#include "../crp_char.cpp"

namespace _01
{
    uint16_t _mem = 0;
    
    void cal(uint8_t port,uint16_t argu)
    {
        if(port == 0x00)//初始化
        {
            //value[_mem]识别此项作为设置

            _mem = argu;
            crp_char::load();
            value[_mem] = 0x0100;//正常
        }
        else if(port == 0x01)//输出单个字符
        {
            
            uint32_t val = 0;
            val = crp_char::utf_8(value[argu]);
            uint8_t* p   = reinterpret_cast<uint8_t*>(&val);
            for (int i = 0; i < 4; ++i) std::putchar(p[i]);
        }

    }


}