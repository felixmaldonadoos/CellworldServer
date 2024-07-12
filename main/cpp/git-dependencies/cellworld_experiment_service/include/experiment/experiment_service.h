#pragma once
#include<tcp_messages.h>
#include<experiment/experiment_messages.h>
#include<agent_tracking/tracking_client.h>
#include<experiment/experiment_client.h>
#include<cell_world.h>

namespace experiment{
    struct Experiment_tracking_client : agent_tracking::Tracking_client {
        void on_step(const cell_world::Step &) override;
        Experiment_server *experiment_server;
    };

    struct Experiment_service : tcp_messages::Message_service {
        Routes(
                Add_route_with_response("start_experiment", start_experiment, Start_experiment_request);
                Add_route_with_response("resume_experiment", resume_experiment, Resume_experiment_request);
                Add_route_with_response("start_episode", start_episode, Start_episode_request);
                Add_route_with_response("finish_episode", finish_episode);
                Add_route_with_response("finish_experiment", finish_experiment, Finish_experiment_request);
                Add_route_with_response("get_experiment", get_experiment, Get_experiment_request);
                Add_route_with_response("capture", capture, Capture_request);
                Add_route_with_response("human_intervention", human_intervention, Human_intervention_request);
                Add_route_with_response("set_behavior", set_behavior, Set_behavior_request);
                Add_route_with_response("prey_enter_arena", prey_enter_arena);
                Add_route_with_response("reward_reached", reward_reached);
                Add_route_with_response("experiment_broadcast", experiment_broadcast, Broadcast_request);
                Allow_subscription();
                )

        Start_experiment_response start_experiment(const Start_experiment_request &);
        Resume_experiment_response resume_experiment(const Resume_experiment_request &);
        bool experiment_broadcast(const Broadcast_request &);
        bool start_episode(const Start_episode_request &);
        bool finish_episode();
        bool finish_experiment(const Finish_experiment_request &);
        bool prey_enter_arena();
        bool reward_reached();
        static Get_experiment_response get_experiment(const Get_experiment_request &);

        static void set_logs_folder(const std::string &path);
        static int get_port();
        bool capture(const Capture_request &);
        bool human_intervention(const Human_intervention_request &);
        bool set_behavior(const Set_behavior_request &);
    };

    struct Experiment_server : tcp_messages::Message_server<Experiment_service> {
        ~Experiment_server();
        Start_experiment_response start_experiment(const Start_experiment_request &);
        Resume_experiment_response resume_experiment(const Resume_experiment_request &);
        bool start_episode(const Start_episode_request &);
        bool finish_episode();
        bool finish_experiment(const Finish_experiment_request &);
        bool capture(const Capture_request &);
        bool human_intervention(const Human_intervention_request &);
        bool set_behavior(const Set_behavior_request &);
        void set_tracking_client(Experiment_tracking_client &);
        bool prey_enter_arena();
        bool reward_reached();


        std::string active_experiment = "";
        cell_world::Episode active_episode;
        bool episode_in_progress = false;
        bool prey_detected = false;
        Experiment_tracking_client *tracking_client = nullptr;
        std::string tracking_service_ip = "";
        float current_time=0;

        template< typename T, typename... Ts>
        T &create_local_client(Ts... vs){
            static_assert(std::is_base_of<Experiment_client, T>::value, "T must inherit from Tracking_client");
            auto new_local_client = new T{ vs... };
            local_clients.push_back((Experiment_client *) new_local_client);
            new_local_client->local_server = this;
            return *new_local_client;
        }

        bool subscribe_local( Experiment_client *client) {
            subscribed_local_clients.push_back(client);
            return true;
        }

        bool unsubscribe_local(Experiment_client *client) {
            subscribed_local_clients.erase(std::remove(subscribed_local_clients.begin(), subscribed_local_clients.end(), client));
            return true;
        }

        bool remove_local_client(Experiment_client *client) {
            subscribed_local_clients.erase(std::remove(subscribed_local_clients.begin(), subscribed_local_clients.end(), client));
            local_clients.erase(std::remove(local_clients.begin(), local_clients.end(), client));
            delete client;
            return true;
        }

        std::vector<Experiment_client * > local_clients;
        std::vector<Experiment_client * > subscribed_local_clients;
        std::mutex step_insertion_mtx;
    };
}