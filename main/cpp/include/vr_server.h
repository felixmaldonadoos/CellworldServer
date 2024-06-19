#pragma once
#include <experiment.h>
#include <agent_tracking.h>
#include <tcp_messages.h>
#include <json_cpp.h>
#include <cell_world.h>

// cannot be made static bc changes way we call the function
namespace vr_server {
    struct Vr_service : tcp_messages::Message_service {
        Routes(
            Add_route_with_response("start_experiment", start_experiment, experiment::Start_experiment_request);
            Add_route_with_response("resume_experiment", resume_experiment, experiment::Resume_experiment_request);
            Add_route_with_response("start_episode", start_episode, experiment::Start_episode_request);
            Add_route_with_response("finish_episode", finish_episode);
            Add_route_with_response("finish_experiment", finish_experiment, experiment::Finish_experiment_request);
            Add_route_with_response("get_experiment", get_experiment, experiment::Get_experiment_request);
            Add_route_with_response("get_cell_locations", get_cell_locations);
            Add_route_with_response("get_occlusions", get_occlusions, std::string);
            Add_route("prey_step", on_prey_step, cell_world::Step);
            )
        experiment::Start_experiment_response start_experiment(experiment::Start_experiment_request &);
        experiment::Resume_experiment_response resume_experiment(experiment::Resume_experiment_request &);
        void on_prey_step(cell_world::Step &);
        bool start_episode(const experiment::Start_episode_request &);
        bool finish_episode();
        bool finish_experiment(const experiment::Finish_experiment_request &);
        experiment::Get_experiment_response get_experiment(const experiment::Get_experiment_request &);
        cell_world::Location_list get_cell_locations();
        cell_world::Cell_group_builder get_occlusions(std::string &);
    };

    struct Vr_server : tcp_messages::Message_server<Vr_service> {
        Vr_server();
        bool prepare();
        void stop();
        void join();
        agent_tracking::Tracking_server tracking_server;
        experiment::Experiment_server experiment_server;
    };
}