#pragma once
#include <json_cpp.h>
#include <cell_world.h>

namespace experiment {

    struct Start_experiment_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(prefix);
                Add_member(suffix);
                Add_member(world);
                Add_member(subject_name);
                Add_member(duration);
                Add_member(rewards_cells);
                Add_member(rewards_orientations);
                )
        std::string prefix;
        std::string suffix;
        cell_world::World_info world;
        std::string subject_name;
        int duration;
        cell_world::Cell_group_builder rewards_cells;
        cell_world::Json_int_vector rewards_orientations;
    };

    struct Start_experiment_response :json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
                Add_member(start_date);
                Add_member(world);
                Add_member(subject_name);
                Add_member(duration);
                Add_optional_member(rewards_cells);
                )
        std::string experiment_name;
        json_cpp::Json_date start_date;
        cell_world::World_info world;
        std::string subject_name;
        cell_world::Cell_group_builder rewards_cells;
        int duration;
    };

    struct Resume_experiment_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
                Add_member(duration_extension);
        )
        std::string experiment_name;
        int duration_extension;
    };

    struct Resume_experiment_response :json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
                Add_member(start_date);
                Add_member(world);
                Add_member(subject_name);
                Add_member(duration);
                Add_member(episode_count);
        )
        std::string experiment_name;
        json_cpp::Json_date start_date;
        cell_world::World_info world;
        std::string subject_name;
        int duration;
        unsigned int episode_count;
    };

    struct Start_episode_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
                Add_optional_member(rewards_sequence);
        )
        std::string experiment_name;
        cell_world::Cell_group_builder rewards_sequence;
    };

    struct Finish_experiment_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
        )
        std::string experiment_name;
    };

    struct Get_experiment_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
        )
        std::string experiment_name;
    };

    struct  Set_behavior_request: json_cpp::Json_object {
        Json_object_members(
                Add_member(behavior);
                )
        int behavior;
    };

    struct Get_experiment_response : json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
                Add_member(world_info);
                Add_member(start_date);
                Add_member(subject_name);
                Add_member(duration);
                Add_member(remaining_time);
                Add_member(episode_count);
                Add_member(rewards_cells);
        )
        std::string experiment_name;
        cell_world::World_info world_info;
        json_cpp::Json_date start_date;
        std::string subject_name;
        unsigned int duration;
        float remaining_time;
        unsigned int episode_count;
        cell_world::Cell_group_builder rewards_cells;
    };

    struct Capture_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(frame);
                )
        unsigned int frame;
    };

    struct Human_intervention_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(active);
        )
        bool active;
    };

    struct Broadcast_request : json_cpp::Json_object{
        Json_object_members(
                Add_member(message_header);
                Add_member(message_body);
        )
        std::string message_header;
        std::string message_body;
    };

    struct Episode_started_message : json_cpp::Json_object{
        Json_object_members(
                Add_member(experiment_name);
                Add_member(rewards_sequence);
        )
        std::string experiment_name;
        cell_world::Cell_group_builder rewards_sequence;
    };
}