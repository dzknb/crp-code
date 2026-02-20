#include <iostream>
#include <fstream>
#include <cstdint>

namespace crp_char
{    
    uint32_t char_data[65536] = {};

    void load()
    {
        std::ifstream file("crp_char.dat",std::ios::binary|std::ios::ate);
        if(!file.is_open())
        {
            std::cout<<"Error,Can't open file"<<std::endl;
        }
        file.seekg(0); // 回到开头
    
        file.read(reinterpret_cast<char*>(char_data),(std::streamsize(sizeof(uint32_t)) * 65536));

    }

    uint32_t utf_8(uint16_t number)
    {
        return char_data[number];
    }





}
