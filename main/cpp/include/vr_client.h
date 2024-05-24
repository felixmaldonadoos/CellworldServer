#pragma once
#include <experiment.h>
#include <tcp_messages.h>
#include <json_cpp.h>
#include <cell_world.h>

namespace vr_client{
    struct Vr_client_service : tcp_messages::Message_client {

    };


    struct Vr_server : tcp_messages::Message_server<Vr_client_service> {
        Vr_server();
        bool prepare();
        void stop();
        void join();
        bool start_experiment(const experiment::Start_experiment_request &);
        agent_tracking::Tracking_server tracking_server;
        experiment::Experiment_server experiment_server;
    };
}