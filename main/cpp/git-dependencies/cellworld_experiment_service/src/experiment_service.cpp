#include <experiment/experiment_service.h>
#include <filesystem>
#include <performance.h>

using namespace tcp_messages;
using namespace cell_world;
using namespace std;

namespace experiment {
    std::string logs_path = "";

    string get_experiment_prefix(const string &experiment_name){
        return experiment_name.substr(0,experiment_name.find('_'));
    }

    string get_experiment_file(const string &experiment_name){
        return logs_path + get_experiment_prefix(experiment_name) + '/' + experiment_name + "/" + experiment_name + "_experiment.json";
    }

    string get_episode_folder(const string &experiment_name, unsigned int episode_number){
        std::stringstream ss;
        ss << "episode_" << std::setw(3) << std::setfill('0') << episode_number;
        auto episode = ss.str();
        return logs_path + get_experiment_prefix(experiment_name) + '/' + experiment_name + "/" + episode;
    }

    string get_episode_file(const string &experiment_name, unsigned int episode_number){
        std::stringstream ss;
        ss << "episode_" << std::setw(3) << std::setfill('0') << episode_number;
        auto episode = ss.str();
        return get_episode_folder(experiment_name, episode_number) +  "/" + experiment_name + "_" + episode + ".json";
    }

    Start_experiment_response Experiment_service::start_experiment(const Start_experiment_request &parameters) {
        PERF_SCOPE("Experiment_service::start_experiment");
        auto server = (Experiment_server *)_server;
        return server->start_experiment(parameters);
    }

    bool Experiment_service::start_episode(const Start_episode_request &parameters) {
        PERF_SCOPE("Experiment_service::start_episode");
        auto server = (Experiment_server *)_server;
        return server->start_episode(parameters);
    }

    bool Experiment_service::reward_reached() {
        PERF_SCOPE("Experiment_service::reward_reached");
        auto server = (Experiment_server *)_server;
        return server->reward_reached();
    }

    bool Experiment_service::finish_episode() {
        PERF_SCOPE("Experiment_service::finish_episode");
        auto server = (Experiment_server *)_server;
        return server->finish_episode();
    }

    bool Experiment_service::finish_experiment(const Finish_experiment_request &parameters) {
        PERF_SCOPE("Experiment_service::finish_experiment");
        auto server = (Experiment_server *)_server;
        return server->finish_experiment(parameters);
    }

    bool Experiment_service::capture(const Capture_request &parameters) {
        PERF_SCOPE("Experiment_service::capture");
        auto server = (Experiment_server *)_server;
        return server->capture(parameters);
    }

    bool Experiment_service::set_behavior(const Set_behavior_request &request) {
        PERF_SCOPE("Experiment_service::set_behavior");
        auto server = (Experiment_server *)_server;
        return server->set_behavior(request);
    }

    bool Experiment_service::prey_enter_arena() {
        PERF_SCOPE("Experiment_service::prey_enter_arena");
        auto server = (Experiment_server *)_server;
        return server->prey_enter_arena();
    }

    Get_experiment_response Experiment_service::get_experiment(const Get_experiment_request &parameters) {
        PERF_SCOPE("Experiment_service::get_experiment");
        Get_experiment_response response;
        if (!cell_world::file_exists(get_experiment_file(parameters.experiment_name))) return response;
        auto experiment = json_cpp::Json_from_file<Experiment>(get_experiment_file(parameters.experiment_name));
        auto end_time = experiment.start_time + chrono::minutes(experiment.duration);
        float remaining = ((float)(end_time - json_cpp::Json_date::now()).count()) / 1000;
        if (remaining<0) remaining = 0;
        response.rewards_cells = experiment.rewards_cells;
        response.world_info.world_configuration = experiment.world_configuration_name;
        response.world_info.world_implementation = experiment.world_implementation_name;
        response.world_info.occlusions = experiment.occlusions;
        response.experiment_name = experiment.name;
        response.start_date = experiment.start_time;
        response.duration = experiment.duration;
        response.episode_count = experiment.episode_count;
        response.remaining_time = remaining;
        response.subject_name = experiment.subject_name;
        return response;
    }

    int Experiment_service::get_port() {
        string port_str(std::getenv("CELLWORLD_EXPERIMENT_SERVICE_PORT") ? std::getenv("CELLWORLD_EXPERIMENT_SERVICE_PORT") : "4540");
        return atoi(port_str.c_str());
    }

    void Experiment_service::set_logs_folder(const string &path) {
        logs_path = path;
        filesystem::create_directory(filesystem::path(logs_path));
    }

    void Experiment_server::set_tracking_client(Experiment_tracking_client &new_tracking_client) {
        new_tracking_client.experiment_server = this;
        tracking_client = &new_tracking_client;

    }

    void Experiment_tracking_client::on_step(const Step &step) {
        std::cout << "Experiment_tracking_client::on_step(const Step &step)\n";
        PERF_SCOPE("Experiment_tracking_client::on_step");
        if (experiment_server->episode_in_progress){
            if (step.agent_name=="prey"){
                experiment_server->prey_detected = true;
            }
            if (experiment_server->prey_detected) {
                experiment_server->step_insertion_mtx.lock();
                experiment_server->active_episode.trajectories.push_back(step);
                experiment_server->step_insertion_mtx.unlock();
                experiment_server->current_time = step.time_stamp;
            }
        }
    }

    bool Experiment_server::start_episode(const Start_episode_request &parameters) {
        PERF_SCOPE("Experiment_server::start_episode");
        if (episode_in_progress) return false;
        if (cell_world::file_exists(get_experiment_file(parameters.experiment_name))){
            active_experiment = parameters.experiment_name;
            active_episode = Episode();
            active_episode.rewards_sequence = parameters.rewards_sequence;
            active_episode.start_time = json_cpp::Json_date::now();
            //active_episode.trajectories.reserve(50000);
            episode_in_progress = true;
            prey_detected = false;
            Episode_started_message message;
            message.experiment_name = active_experiment;
            message.rewards_sequence = parameters.rewards_sequence;
            thread( [this]( auto message) {
                if (!clients.empty()) broadcast_subscribed(tcp_messages::Message("episode_started", message));
                for (auto &local_client: subscribed_local_clients) local_client->on_episode_started(active_experiment);
            }, message).detach();
            return true;
        }
        return false;
    }

    bool Experiment_server::finish_episode() {
        PERF_SCOPE("Experiment_server::finish_episode");
        if (!episode_in_progress) return false;
        episode_in_progress = false;
        if (!cell_world::file_exists(get_experiment_file(active_experiment))) return false;
        auto experiment = json_cpp::Json_from_file<Experiment>(get_experiment_file(active_experiment));
        active_episode.end_time = json_cpp::Json_date::now();
        //experiment.episodes.push_back(active_episode);
        create_folder(get_episode_folder(active_experiment, experiment.episode_count));
        active_episode.save(get_episode_file(active_experiment, experiment.episode_count));
        experiment.episode_count++;
        experiment.save(get_experiment_file(active_experiment));
        if (!clients.empty()) broadcast_subscribed(tcp_messages::Message("episode_finished",active_experiment));
        for (auto &local_client:subscribed_local_clients) local_client->on_episode_finished();
        return true;
    }

    bool Experiment_server::finish_experiment(const Finish_experiment_request &parameters) {
        PERF_SCOPE("Experiment_server::finish_experiment");
        if (!cell_world::file_exists(get_experiment_file(active_experiment))) {
            return false;
        }
        auto experiment = json_cpp::Json_from_file<Experiment>(get_experiment_file(parameters.experiment_name));
        auto end_time = experiment.start_time + chrono::minutes(experiment.duration);
        float remaining = ((float)(end_time - json_cpp::Json_date::now()).count()) / 1000;
        if (remaining>0){
            experiment.duration = (unsigned int) (((float)(json_cpp::Json_date::now() - experiment.start_time).count()) / 1000 / 60);
            experiment.save(get_experiment_file(parameters.experiment_name));
        }
        if (!clients.empty()) broadcast_subscribed(tcp_messages::Message("experiment_finished",parameters.experiment_name));
        for (auto &local_client:subscribed_local_clients) local_client->on_experiment_finished(parameters.experiment_name);
        return true;
    }

    bool Experiment_server::capture(const Capture_request &request) {
        PERF_SCOPE("Experiment_server::capture");
        if (episode_in_progress) {
            active_episode.captures.push_back(request.frame);
            if (!clients.empty()) broadcast_subscribed(Message("capture",request.frame));
            for (auto &local_client:subscribed_local_clients) local_client->on_capture(request.frame);
            return true;
        }
        return false;
    }

    bool Experiment_server::set_behavior(const Set_behavior_request &request) {
        PERF_SCOPE("Experiment_server::set_behavior");
        if (!clients.empty()) broadcast_subscribed(Message("behavior_set", request.behavior));
        for (auto &local_client:subscribed_local_clients) local_client->on_behavior_set(request.behavior);
        return true;
    }

    bool Experiment_server::prey_enter_arena() {
        PERF_SCOPE("Experiment_server::prey_enter_arena");
        if (!clients.empty()) broadcast_subscribed(Message("prey_entered_arena"));
        for (auto &local_client:subscribed_local_clients) local_client->on_prey_entered_arena();
        return true;
    }

    bool Experiment_server::reward_reached() {
        PERF_SCOPE("Experiment_server::reward_reached");
        if (!clients.empty()) broadcast_subscribed(Message("reward_reached"));
        active_episode.rewards_time_stamps.push_back(current_time);
        for (auto &local_client:subscribed_local_clients) local_client->on_prey_entered_arena();
        return true;
    }

    Experiment_server::~Experiment_server() {
        for (auto local_client: local_clients){
            delete local_client;
        }
    }

    Start_experiment_response Experiment_server::start_experiment(const Start_experiment_request &parameters) {
        PERF_SCOPE("Experiment_server::start_experiment");
        std::filesystem::create_directories(logs_path + '/' + parameters.prefix);
        Experiment new_experiment;
        new_experiment.world_configuration_name = parameters.world.world_configuration;
        new_experiment.world_implementation_name = parameters.world.world_implementation;
        new_experiment.occlusions = parameters.world.occlusions;
        new_experiment.duration = parameters.duration;
        new_experiment.subject_name = parameters.subject_name;
        new_experiment.start_time = json_cpp::Json_date::now();
        new_experiment.rewards_cells = parameters.rewards_cells;
        new_experiment.rewards_orientations = parameters.rewards_orientations;
        new_experiment.set_name(parameters.prefix, parameters.suffix);
        std::filesystem::create_directories(logs_path + '/' + parameters.prefix + "/" + new_experiment.name);
        new_experiment.save(get_experiment_file(new_experiment.name));
        Start_experiment_response response;
        response.experiment_name = new_experiment.name;
        response.start_date = new_experiment.start_time;
        response.subject_name = parameters.subject_name;
        response.world = parameters.world;
        response.duration = parameters.duration;
        response.rewards_cells = parameters.rewards_cells;
        if (!clients.empty()) broadcast_subscribed(tcp_messages::Message("experiment_started",response));
        for (auto &local_client:subscribed_local_clients) local_client->on_experiment_started(response);
        return response;
    }

    bool Experiment_service::human_intervention(const Human_intervention_request &request) {
        PERF_SCOPE("Experiment_service::human_intervention");
        auto server = (Experiment_server *)_server;
        return server->prey_enter_arena();
    }

    bool Experiment_server::human_intervention(const Human_intervention_request &request) {
        PERF_SCOPE("Experiment_server::human_intervention");
        if (!clients.empty()) broadcast_subscribed(tcp_messages::Message("human_intervention",request));
        for (auto &local_client:subscribed_local_clients) local_client->on_human_intervention(request.active);
        return false;
    }

    Resume_experiment_response Experiment_service::resume_experiment(const Resume_experiment_request &parameters) {
        PERF_SCOPE("Experiment_service::resume_experiment");
        auto server = (Experiment_server *)_server;
        return server->resume_experiment(parameters);
    }

    Resume_experiment_response Experiment_server::resume_experiment(const Resume_experiment_request &parameters) {
        PERF_SCOPE("Experiment_server::resume_experiment");
        Resume_experiment_response r;
        if (cell_world::file_exists(get_experiment_file(parameters.experiment_name))){
            active_experiment = parameters.experiment_name;
            auto experiment = json_cpp::Json_from_file<Experiment>(get_experiment_file(active_experiment));
            // state the interruption as an empty episode
            auto interruption_start_time = experiment.start_time;
            if  (experiment.episode_count > 0){
                auto last_episode =  json_cpp::Json_from_file<Episode>(get_episode_file(active_experiment, experiment.episode_count - 1));
                interruption_start_time = last_episode.end_time;
            }
            active_episode = Episode();
            active_episode.start_time = interruption_start_time;
            active_episode.end_time = json_cpp::Json_date::now();
            create_folder(get_episode_folder(active_experiment, experiment.episode_count));
            active_episode.save(get_episode_file(active_experiment, experiment.episode_count));
            experiment.episode_count ++;
            //experiment.episodes.push_back(active_episode);
            //
            experiment.duration += parameters.duration_extension;
            experiment.save(get_experiment_file(active_experiment)); // saves the interruption and the extension to file
            r.experiment_name = parameters.experiment_name;
            r.world.world_configuration = experiment.world_configuration_name;
            r.world.world_implementation = experiment.world_implementation_name;
            r.world.occlusions = experiment.occlusions;
            r.duration = experiment.duration;
            r.start_date = experiment.start_time;
            r.subject_name = experiment.subject_name;
            r.episode_count = experiment.episode_count;
            episode_in_progress = false;
            if (!clients.empty()) broadcast_subscribed(tcp_messages::Message("experiment_resumed",r));
            for (auto &local_client:subscribed_local_clients) local_client->on_experiment_resumed(r);
            return r;
        }
        return r;
    }

    bool Experiment_service::experiment_broadcast(const Broadcast_request &broadcast_request) {
        broadcast_subscribed(Message(broadcast_request.message_header, broadcast_request.message_body));
        return true;
    }

}