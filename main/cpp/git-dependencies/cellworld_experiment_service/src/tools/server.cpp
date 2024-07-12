#include <experiment.h>
#include <params_cpp.h>

using namespace std;
using namespace tcp_messages;
using namespace experiment;
using namespace params_cpp;

int main (int argc, char **argv){
    Parser parser(argc,argv);
    Key tracking_service_ip_key("-tip", "-tracking_ip", "-tracking_service_ip");
    Key logs_path_key("-l", "-logs", "-logs_path");
    Experiment_server server;
    Experiment_service::set_logs_folder(parser.get(logs_path_key,"experiment_logs/"));
    auto tracking_service_ip = parser.get(tracking_service_ip_key, "");
    Experiment_tracking_client tracking_client;
    if (tracking_client.connect(tracking_service_ip))
        server.set_tracking_client(tracking_client);
    server.start(Experiment_service::get_port());
    server.join();
}
