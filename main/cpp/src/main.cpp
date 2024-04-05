#include <vr_server.h>

using namespace vr_server;
using namespace std;

int main(int argc, char **argv){
    Vr_server my_server;
    my_server.prepare();
    my_server.start(4566);
    cout << "server running" << endl;
    my_server.join();
}