#include <catch.h>
#include <experiment.h>
#include <thread>

using namespace cell_world;
using namespace experiment;
using namespace std;
using namespace this_thread;

struct Client : experiment::Experiment_client {
    void on_experiment_started(const Start_experiment_response &experiment) override{
        cout << t << ": " << "on_experiment_started: " <<  experiment << endl;
    }
    void on_episode_started(const std::string &experiment_name) override {
        cout << t << ": " << "on_episode_started: " <<  experiment_name << endl;
    }
    void on_episode_finished() override{
        cout << t << ": " << "on_episode_finished: " << endl;
    }
    void on_experiment_finished(const std::string &experiment_name) override{
        cout << t << ": " << "on_experiment_finished: " <<  experiment_name << endl;
        disconnect();
    }
    string t;
};

//TEST_CASE("client_test") {
//    auto t1 = thread ([]() {
//        Client client;
//        client.t = "INNER";
//        client.connect("127.0.0.1");
//        client.subscribe();
//        client.join();
//    });
//    World_info wi;
//    wi.world_configuration = "hexagonal";
//    wi.world_implementation = "cv";
//    wi.occlusions = "10_05";
//    Client client;
//    client.connect("127.0.0.1");
//    client.t = "OUTER";
//    //client.subscribe();
//    sleep_for(1s);
//    auto experiment = client.start_experiment(wi,"test_subject",60,"prefix","suffix");
//    while (client.is_active(experiment.experiment_name)) {
//        sleep_for(1s);
//        cout << "starting episode" << endl;
//        client.start_episode(experiment.experiment_name);
//        sleep_for(1s);
//        cout << "finishing episode" << endl;
//        client.finish_episode();
//    }
//    sleep_for(1s);
//    client.finish_experiment(experiment.experiment_name);
//    sleep_for(1s);
//    client.disconnect();
//    t1.join();
//}

TEST_CASE("local client_test") {
    Experiment_server server;
    Experiment_service::set_logs_folder("experiment_logs/");
    server.start(Experiment_service::get_port());

    auto t1 = thread ([](Experiment_server &server) {
        auto &client = server.create_local_client<Client>();
        client.t = "INNER";
        client.subscribe();
        client.join();
    }, std::ref(server));

    World_info wi;
    wi.world_configuration = "hexagonal";
    wi.world_implementation = "cv";
    wi.occlusions = "10_05";
    auto &client = server.create_local_client<Client>();
    client.t = "OUTER";
    client.subscribe();
    auto experiment = client.start_experiment(wi,"test_subject",1,"prefix","suffix");
    while (client.is_active(experiment.experiment_name)) {
        cout << "starting episode" << endl;
        client.start_episode(experiment.experiment_name);
        cout << "finishing episode" << endl;
        client.finish_episode();
    }
    sleep_for(1s);
    client.finish_experiment(experiment.experiment_name);
    sleep_for(1s);
}

//
//template< typename T, typename... Ts>
//T Make(Ts... vs) {
//    return T{ vs... };
//}
//
//TEST_CASE("variadic"){
//    cout << Make<Coordinates>() << endl;
//}