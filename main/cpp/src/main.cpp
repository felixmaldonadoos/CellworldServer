#include <vr_server.h>

using namespace vr_server;

//constexpr int PORT = 4566;
constexpr int PORT = 4970;

int main(int argc, char **argv){
    Vr_server my_server;
    my_server.prepare();
    my_server.start(PORT);
//    my_server.
    std::cout << "Started server on port: " << PORT << std::endl;
    my_server.join();

}