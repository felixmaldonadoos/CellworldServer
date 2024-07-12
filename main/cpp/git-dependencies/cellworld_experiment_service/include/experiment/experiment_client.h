#pragma once
#include <experiment/experiment_messages.h>
#include <tcp_messages.h>
#include <cell_world.h>

namespace experiment {
    struct Experiment_server;

    struct Experiment_client : tcp_messages::Message_client {

        Routes(
                Add_route("experiment_started", on_experiment_started, Start_experiment_response);
                Add_route("episode_started", on_episode_started, std::string);
                Add_route("experiment_resumed", on_experiment_resumed, Resume_experiment_response);
                Add_route("episode_finished", on_episode_finished);
                Add_route("experiment_finished", on_experiment_finished, std::string);
                Add_route("behavior_set", on_behavior_set, int);
                Add_route("capture", on_capture, int);
                Add_route("prey_entered_arena", on_prey_entered_arena);
        )

        virtual void on_experiment_started(const Start_experiment_response &) {};

        virtual void on_experiment_resumed(const Resume_experiment_response &) {};

        virtual void on_episode_started(const std::string &) {};

        virtual void on_episode_finished() {};

        virtual void on_experiment_finished(const std::string &) {};

        virtual void on_behavior_set(int) {};

        virtual void on_prey_entered_arena() {};

        virtual void on_capture(int){};

        virtual void on_human_intervention(bool){};

        Start_experiment_response start_experiment(const cell_world::World_info &world, const std::string &subject_name, int duration,
                         const std::string &prefix = "", const std::string &suffix = "");

        Resume_experiment_response resume_experiment(const std::string &experiment_name, unsigned int duration_extension);

        bool start_episode(const std::string &experiment_name);

        bool finish_episode();

        bool finish_experiment(const std::string &experiment_name);


        Get_experiment_response get_experiment(const std::string &experiment_name);

        bool is_active(const std::string &experiment_name);

        bool connect (const std::string &ip);

        bool capture(unsigned int frame);

        bool human_intervention(bool);

        bool set_behavior(int behavior);

        bool prey_enter_arena();

        Experiment_server *local_server = nullptr;

        bool subscribe();

        bool unsubscribe();

        bool experiment_broadcast(const tcp_messages::Message &message);

        virtual ~Experiment_client() = default;
    };
}