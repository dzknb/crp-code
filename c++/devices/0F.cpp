#include<iostream>
#include<cstdint>

namespace _0F //时钟
{
    uint16_t _mem = 0;
    uint16_t _tick = 0;

    void cal(uint8_t port,uint16_t argu)
    {
        switch (port)
        {
        case 0x00: //设置返回
            _mem = argu;
            value[_mem] = 0x0F00;
            break;
        
        case 0x01: //返回tick
            value[_mem] = _tick;
            
            break;

        default:
            break;
        }
    }

    void tick()
    {
        _tick += 1;
    }


}