#include "0F.cpp"
#include "01.cpp"
#include<cstdint>

namespace _FF //总设备控制器
{
    uint16_t _mem = 0;

    void cal(uint8_t number,uint8_t port,uint16_t argu)
    {
        switch (number)
        {
        case 0xFF:
            if(port == 0x00)
            {
                _mem = argu;
                value[_mem] = 0xFF00;//正常
            }
            else if(port == 0xFF)//硬件时钟触发
            {
                _0F::tick(); //时钟
            }
            break;
            
        
        case 0x01:
            _01::cal(port,argu);
            break;
            
        
        case 0x0F:
            _0F::cal(port,argu);
            break;

        default:
            break;
        }

    }

}
