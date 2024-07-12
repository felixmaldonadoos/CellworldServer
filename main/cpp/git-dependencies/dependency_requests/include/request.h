#pragma once
#include <iostream>
#include <curl/curl.h>
#include "response.h"
#define Web_get(URL, ...) requests::Request(requests::URI(URL)).get_response()__VA_OPT__(.get<__VA_ARGS__>())

namespace requests {

    struct URI {
        URI();
        explicit URI(const std::string &);
        enum Protocol{
            http,
            https
        };
        Protocol protocol;
        std::string domain;
        unsigned int port;
        std::string query_string;
        std::string url() const;
        friend std::ostream & operator << (std::ostream & , const URI &);
    };

    struct Request {
        explicit Request(URI);
        Response get_response();
    private:
        URI uri;
    };
}