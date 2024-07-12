#include <response.h>
#include <unistd.h>

using namespace std;

namespace requests {

    string Response::get_string() const {
        std::stringstream buffer;
        buffer << ifs.rdbuf();
        return buffer.str();
    }

    ostream &operator<<(ostream &o, Response &r) {
        o << r.get_stream().rdbuf();
        return o;
    }

    std::istream &Response::get_stream() {
        return ifs;
    }

    Response::Response(const string &file_path, const string &url) :
        _file_path(file_path),
        url(url){
        ifs.open (_file_path.c_str(), std::ifstream::in);
    }

    Response::~Response() {
        unlink(_file_path.c_str());

    }

    void Response::save(const string &file_name) {
        ofstream dest(file_name.c_str());
        dest << ifs.rdbuf();
        dest.close();
    }
}


