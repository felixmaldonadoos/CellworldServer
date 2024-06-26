#include "vr_server.h"

//todo: function to get number of active connections

bool vr_server::Vr_server::prepare() {
    tracking_server.start(agent_tracking::Tracking_service::get_port());
    auto &experiment_tracking_client = tracking_server.create_local_client<experiment::Experiment_tracking_client>();
    experiment_tracking_client.subscribe();
    experiment_server.set_tracking_client(experiment_tracking_client);
    experiment::Experiment_service::set_logs_folder("../logs/");
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

    return cell_locations;
}

cell_world::Cell_group_builder vr_server::Vr_service::get_occlusions(std::string &occlusion_name) {
//    std::cout << cell_world::Resources::from("cell_group").key("hexagonal").key(occlusion_name).key("occlusions").get_resource<cell_world::Cell_group_builder>().to_json() << "\n";
    return cell_world::Resources::from("cell_group").key("hexagonal").key(occlusion_name).key("occlusions").get_resource<cell_world::Cell_group_builder>();
}

// relay routes you want to use
experiment::Start_experiment_response vr_server::Vr_service::start_experiment(experiment::Start_experiment_request & request) {

    experiment::Start_experiment_response response = ((Vr_server *) this->_server)->experiment_server.start_experiment(request);
    std::cout << "START EXPERIMENT RESPONSE: " << response.experiment_name << std::endl;
    return response;
}

bool vr_server::Vr_service::finish_experiment(const experiment::Finish_experiment_request &request) {
    bool response = ((Vr_server *) this->_server)->experiment_server.finish_experiment(request);
    std::cout << "FINISH EXPERIMENT RESPONSE: " << response << std::endl;
    return response;
}

experiment::Resume_experiment_response vr_server::Vr_service::resume_experiment(experiment::Resume_experiment_request & request) {
    std::cout << "RESUME EXPERIMENT NOT SET UP YET! SENDING DEFAULT RESPONSE!\n";
    return experiment::Resume_experiment_response();
}

bool vr_server::Vr_service::start_episode(const experiment::Start_episode_request & request) {
    bool response = ((Vr_server *) this->_server)->experiment_server.start_episode(request);
    std::cout << "START EPISODE RESPONSE: " << response << std::endl;
    return response;
}

bool vr_server::Vr_service::finish_episode() {
    bool response = ((Vr_server *) this->_server)->experiment_server.finish_episode();
    std::cout << "FINISH EPISODE RESPONSE: " << response << std::endl;
    return response;
}

experiment::Get_experiment_response vr_server::Vr_service::get_experiment(const experiment::Get_experiment_request & request) {
    std::cout << "GET EXPERIMENT NOT SET UP YET! SENDING DEFAULT RESPONSE!\n";
    return experiment::Experiment_service::get_experiment(request);
}

void vr_server::Vr_service::process_on_step(const cell_world::Step & step) {
    ((Vr_server *) this->_server)->experiment_server.tracking_client->on_step(step);
}

void vr_server::Vr_service::on_prey_step(cell_world::Step & step) {
    std::cout << "RECEIVED STEP: " << step.location << std::endl;
    this->process_on_step(step);
    tcp_messages::Message message;

//    message.header = "predator_step";
//    // todo: implement PC
//    message.body = step.to_json();
//    this->send_message(message);
}

// todo: struct that manages experiment queue

void vr_server::Vr_service::on_connect() {
    std::cout << "ON CONNECT!\n";
    Service::on_connect();
}

void vr_server::Vr_service::on_episode_started(const std::string & episode_started_message) {
    std::cout << "ON EPISODE STARTED:" << episode_started_message << std::endl;
}


void vr_server::Vr_tracking_client::on_step(const cell_world::Step & step) {
    std::cout << "ON STEP vr_server::Vr_tracking_client::on_step(const cell_world::Step & step)!"<< step.location << "\n";
    Experiment_tracking_client::on_step(step);
}
