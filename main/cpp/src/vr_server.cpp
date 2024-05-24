#include "vr_server.h"

bool vr_server::Vr_server::prepare() {
    tracking_server.start(agent_tracking::Tracking_service::get_port());
    auto &experiment_tracking_client = tracking_server.create_local_client<experiment::Experiment_tracking_client>();
    experiment_tracking_client.subscribe();
    experiment_server.set_tracking_client(experiment_tracking_client);
    experiment::Experiment_service::set_logs_folder("../logs");
//    experiment_server.start(experiment::Experiment_service::get_port());
//    std::cout << "experiment_service port: "<< experiment::Experiment_service::get_port() << std::endl;

    return true;
}

void vr_server::Vr_server::stop() {
    experiment_server.stop();
    tracking_server.stop();
}

vr_server::Vr_server::Vr_server() {
    std::cout << __func__ << "\n";
}

void vr_server::Vr_server::join() {
    experiment_server.join();
    tracking_server.join();
}

cell_world::Location_list vr_server::Vr_service::get_cell_locations() {
    auto configuration = cell_world:: Resources::from("world_configuration").key("hexagonal").get_resource<cell_world::World_configuration>();
    auto implementation = cell_world::Resources::from("world_implementation").key("hexagonal").key("canonical").get_resource<cell_world::World_implementation>();
    auto world = cell_world::World(configuration, implementation);
    cell_world::Location_list cell_locations;
    for (cell_world::Cell &cell: world.cells){
        cell_locations.push_back(cell.location);
    }

    std::cout << cell_locations.to_json() << std::endl;
    return cell_locations;
}

cell_world::Cell_group_builder vr_server::Vr_service::get_occlusions(std::string &occlusion_name) {
    std::cout << cell_world::Resources::from("cell_group").key("hexagonal").key(occlusion_name).key("occlusions").get_resource<cell_world::Cell_group_builder>().to_json() << "\n";
    return cell_world::Resources::from("cell_group").key("hexagonal").key(occlusion_name).key("occlusions").get_resource<cell_world::Cell_group_builder>();
}

// relay routes you want to use
experiment::Start_experiment_response vr_server::Vr_service::start_experiment(experiment::Start_experiment_request request) {
    std::cout << "RECEIVED " << request <<  std::endl;
    auto response = ((Vr_server *) this->_server)->experiment_server.start_experiment(request);
    std::cout << "RESPONSE " << response <<  std::endl;
    return response;
}
