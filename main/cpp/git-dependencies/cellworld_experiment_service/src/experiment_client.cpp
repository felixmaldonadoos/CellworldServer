#include <experiment/experiment_client.h>
#include <experiment/experiment_service.h>
#include <experiment/experiment_messages.h>
#include <cell_world.h>
#include <vector>
#include <algorithm>

using namespace cell_world;
using namespace tcp_messages;
using namespace std;

namespace experiment {
    Start_experiment_response Experiment_client::start_experiment(const cell_world::World_info &world, const std::string &subject_name, int duration,
                                                   const std::string &prefix , const std::string &suffix) {
        auto parameters = Start_experiment_request();
        parameters.prefix = prefix;
        parameters.suffix = suffix;
        parameters.world = world;
        parameters.subject_name = subject_name;
        parameters.duration = duration;
        if (local_server) {
            return local_server->start_experiment(parameters);
        } else {
            return send_request(tcp_messages::Message("start_experiment",parameters),0).get_body<Start_experiment_response>();
        }
    }

    bool Experiment_client::start_episode(const std::string &experiment_name) {
        auto parameters = Start_episode_request();
        parameters.experiment_name = experiment_name;
        if (local_server) {
            return local_server->start_episode(parameters);
        } else {
            return send_request(tcp_messages::Message("start_episode", parameters), 0).get_body<bool>();
        }
    }

    bool Experiment_client::finish_episode() {
        if (local_server) {
            return local_server->finish_episode();
        } else {
            return send_request(tcp_messages::Message("finish_episode"),0).get_body<bool>();
        }
    }

    bool Experiment_client::finish_experiment(const std::string &experiment_name) {
        auto parameters = Finish_experiment_request();
        parameters.experiment_name = experiment_name;
        if (local_server) {
            return local_server->finish_experiment(parameters);
        } else {
            return send_request(tcp_messages::Message("finish_experiment",parameters),0).get_body<bool>();
        }
    }

    bool Experiment_client::is_active(const std::string &experiment_name) {
        Get_experiment_response response = get_experiment(experiment_name);
        return response.remaining_time > 0;
    }

    Get_experiment_response Experiment_client::get_experiment(const std::string &experiment_name) {
        Get_experiment_request request;
        request.experiment_name = experiment_name;
        if (local_server) {
            return Experiment_service::get_experiment(request);
        } else {
            return send_request(tcp_messages::Message("get_experiment",request),0).get_body<Get_experiment_response>();
        }
    }

    bool Experiment_client::connect(const std::string &ip) {
        auto port = Experiment_service::get_port();
        return tcp_messages::Message_client::connect(ip, port);
    }

    bool Experiment_client::capture(unsigned int frame) {
        Capture_request request;
        request.frame = frame;
        if (local_server) {
            return local_server->capture(request);
        } else {
            return send_request(Message("capture",request)).get_body<bool>();
        }
    }

    bool Experiment_client::set_behavior(int behavior) {
        Set_behavior_request request;
        request.behavior = behavior;
        if (local_server) {
            return local_server->set_behavior(request);
        } else {
            return send_request(Message("set_behavior",request)).get_body<bool>();
        }
    }


    bool Experiment_client::subscribe() {
        if (local_server) {
            return local_server->subscribe_local(this);

        } else {
            return Message_client::subscribe();
        }
    }

    bool Experiment_client::unsubscribe() {
        if (local_server) {
            return local_server->unsubscribe_local(this);

        } else {
            return Message_client::unsubscribe();
        }
    }

    bool Experiment_client::prey_enter_arena() {
        if (local_server) {
            return local_server->prey_enter_arena();

        } else {
            return send_request(Message("prey_enter_arena")).get_body<bool>();
        }
    }

    bool Experiment_client::human_intervention(bool active) {
        Human_intervention_request r;
        r.active = active;
        if (local_server) {
            return local_server->human_intervention(r);
        } else {
            return send_request(Message("human_intervention", r)).get_body<bool>();
        }
    }

    Resume_experiment_response
    Experiment_client::resume_experiment(const string &experiment_name, unsigned int duration_extension) {
        Resume_experiment_request r;
        r.experiment_name = experiment_name;
        if (local_server) {
            return local_server->resume_experiment(r);
        } else {
            return send_request(Message("resume_experiment", r)).get_body<Resume_experiment_response>();
        }
    }

    bool Experiment_client::experiment_broadcast(const tcp_messages::Message &message) {
        if (local_server) {
            local_server->broadcast_subscribed(message);
            return true;
        } else {
            Broadcast_request r;
            r.message_header = message.header;
            r.message_body = message.body;
            return send_request(Message("experiment_broadcast", r)).get_body<bool>();
        }
    }
}