#include <json_cpp/json_buffer.h>
#include <malloc.h>

namespace json_cpp{

    Json_buffer::~Json_buffer() {
        if (managed) {
            free (address);
        }
    }

    bool Json_buffer::reserve(size_t desired_size) {
        if (size < desired_size){ //finds out if it can reuse the buffer
            if (address) free(address); // frees previously reserved memory
            address = malloc(desired_size);
            if (address == nullptr) return false; //failed to reserve memory for the content
            managed = true;
        }
        size = desired_size;
        return true;
    }

    Json_buffer::Json_buffer(): Json_buffer(false){

    }
    Json_buffer::Json_buffer(bool managed): address(nullptr), size(0), managed(managed) {

    }

    Json_buffer Json_buffer::new_buffer(void * address, size_t size, bool managed ) {
        Json_buffer b(managed);
        b.address = address;
        b.size = size;
        return b;
    }
}
