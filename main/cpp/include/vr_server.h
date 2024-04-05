#pragma once
#include <experiment.h>
#include <agent_tracking.h>
#include <tcp_messages.h>
#include <json_cpp.h>
#include <cell_world.h>

namespace vr_server {
    struct Vr_service : tcp_messages::Message_service {
        Routes(
                Add_route_with_response("get_cell_locations", get_cell_locations);
                Add_route_with_response("get_occlusions", get_occlusions, std::string);
        )
        cell_world::Location_list get_cell_locations();
        cell_world::Cell_group_builder get_occlusions(std::string &);
    };

    struct Vr_server : tcp_messages::Message_server<Vr_service> {
        Vr_server();
        bool prepare();
        void stop();
        void join();
        bool start_experiment(const experiment::Start_experiment_request &);
        agent_tracking::Tracking_server tracking_server;
        experiment::Experiment_server experiment_server;
    };
}