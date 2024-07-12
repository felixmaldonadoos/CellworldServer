#include <catch.h>
#include <json_cpp.h>
#include <iostream>
#include <cstring>

using namespace json_cpp;
using namespace std;

TEST_CASE("basic wrapper"){
    int v = 50;
    Json_object_wrapper<int> i(v);
    string s = "25";
    stringstream ist(s);
    ist >> i;
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(v==25);
    CHECK(r=="25");
}

TEST_CASE("basic const wrapper bool"){
    const bool v = false;
    auto i = json_cpp::Json_object_wrapper<bool>(v);
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(r=="false");

    string s = "true";
    stringstream ist(s);
    CHECK_THROWS(ist >> i);
}

TEST_CASE("basic enum wrapper"){
    enum Enum{
        a,b,c
    };
    Enum v = b;
    auto i = json_cpp::Json_object_wrapper<Enum>(v);
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(r=="1");
    string s = "2";
    stringstream ist(s);
    ist >> i;
    CHECK(v==Enum::c);
}


TEST_CASE("basic wrapper string"){
    string v = "hello";
    Json_object_wrapper<string> i(v);
    string s = "\"bye\"";
    stringstream ist(s);
    ist >> i;
    stringstream o;
    o << i;
    string r;
    o >> r;
    string s2 = "\"bye\"";

    CHECK(v=="bye");
    CHECK(r=="\"bye\"");
}


TEST_CASE("escape sequences"){
    string v = "hello";
    Json_object_wrapper<string> i(v);
    string s = "\"\\\"bye\\n\\\"\"";
    stringstream ist(s);
    ist >> i;
    stringstream o;
    o << i;
    CHECK(v=="\"bye\n\"");
    CHECK(o.str()=="\"\\\"bye\\n\\\"\""); //adds quotation
}

TEST_CASE("more escape sequences"){
    string v = "hello";
    Json_object_wrapper<string> i(v);
    string s = "\"\\x8E - this is a problem ?bye\"";
    stringstream ist(s);
    ist >> i;
    stringstream o;
    o << i;
    CHECK(v=="\x8E - this is a problem ?bye");
    CHECK(o.str()=="\"\\x8E - this is a problem \\?bye\""); //adds quotation
}


TEST_CASE("json builder"){
    int i = 10;
    string s = "hello";
    Json_builder jb;
    Add_member(i);
    Add_member(s);
    string json = "{\"i\":20,\"s\":\"bye\"}";
    stringstream ist(json);
    ist >> jb;
    CHECK(i==20);
    CHECK(s=="bye");
    stringstream o;
    o << jb;
    string r;
    o >> r;
    CHECK(r==json);

}

TEST_CASE("json object"){
    struct Test_json_object: Json_object {
        Test_json_object(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                             Ignore_member("g");
                             Ignore_member("p");
                         })
    };
    Test_json_object tjo {1,"hello"};
    string json = "{\"i\":20,\"s\":\"bye\", \"g\":{\"j\":5}, \"p\": \"hello\"}";
    stringstream ist(json);
    ist >> tjo;
    stringstream o;
    o << tjo;
    string r;
    o >> r;
    CHECK(r=="{\"i\":20,\"s\":\"bye\"}");
    const Test_json_object tjo2{1,"hello"};
    stringstream o2;
    o2 << tjo2;
    string r2;
    o2 >> r2;
    CHECK(r2=="{\"i\":1,\"s\":\"hello\"}");
}

TEST_CASE("json object 2"){
    struct Test_json_object: Json_object {
        Test_json_object(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
                                Add_member(i);
                                Add_member(s);
                                Ignore_additional_members();
                            })
    };
    Test_json_object tjo {1,"hello"};
    string json = "{\"i\":20,\"s\":\"bye\", \"g\":546, \"p\": \"hello\"}";
    stringstream ist(json);
    ist >> tjo;
    stringstream o;
    o << tjo;
    string r;
    o >> r;
    CHECK(r=="{\"i\":20,\"s\":\"bye\"}");
    const Test_json_object tjo2{1,"hello"};
    stringstream o2;
    o2 << tjo2;
    string r2;
    o2 >> r2;
    CHECK(r2=="{\"i\":1,\"s\":\"hello\"}");
}

TEST_CASE("json nested object"){
    struct Test_member: Json_object {
        Test_member(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
            Add_member(i);
            Add_member(s);
        })
    };
    struct Test_json_object: Json_object {
        Test_json_object(int i, string s, Test_member m): i(i), s(s), m(m) {}
        int i;
        string s;
        Test_member m;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                             Add_member(m);
                         })
    };
    Test_member tm {20,"bye"};
    Test_json_object tjo {1,"hello", {20,"bye"}};
    string json = "{\"i\":20,\"s\":\"bye\",\"m\":{\"i\":200,\"s\":\"hello\"}}";
    stringstream ist(json);
    ist >> tjo;
    stringstream o;
    o << tjo;
    string r;
    o >> r;
    CHECK(r==json);
}

TEST_CASE("int list"){
    Json_vector<int> i;
    i.push_back(1);
    i.push_back(2);
    i.push_back(3);
    string json = "[4,5,6]";
    stringstream ist(json);
    ist >> i;
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(r==json);
}

TEST_CASE("double list"){
    Json_vector<double> i;
    i.push_back(-1.5);
    i.push_back(2.5);
    i.push_back(3.5);
    string json = "[-4.5,5.5,6.5]";
    stringstream ist(json);
    ist >> i;
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(r==json);
}

TEST_CASE("bool list"){
    Json_vector<bool> i;
    i.push_back(true);
    i.push_back(false);
    i.push_back(true);
    string jsoni = "[0,1,0]";
    string json = "[false,true,false]";
    stringstream ist(jsoni);
    ist >> i;
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(r==json);
}

TEST_CASE("object list"){
    struct Test_json_object: Json_object {
        Test_json_object(){};
        Test_json_object(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                         })
    };
    Json_vector<Test_json_object> i;
    i.push_back({1,"1"});
    i.push_back({2,"2"});
    i.push_back({3,"3"});
    string json = "[{\"i\":4,\"s\":\"4\"},{\"i\":5,\"s\":\"5\"},{\"i\":6,\"s\":\"6\"}]";
    stringstream ist(json);
    ist >> i;
    stringstream o;
    o << i;
    string r;
    o >> r;
    CHECK(r==json);
}

TEST_CASE("nested object list"){
    struct Test_member: Json_object {
        Test_member(){};
        Test_member(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                         })
    };
    struct Test_json_object: Json_object {
        Test_json_object(){};
        Test_json_object(int i, string s, Test_member m): i(i), s(s), m(m) {}
        int i;
        string s;
        Test_member m;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                             Add_member(m);
                         })
    };
    Test_json_object o {1,"1",{2, "2"}};
    Json_vector<Test_json_object> i;
    i.push_back({1,"1",{1,"1"}});
    i.push_back({2,"2",{1,"1"}});
    i.push_back({3,"3",{1,"1"}});
    string json = "[{\"i\":4,\"s\":\"4\",\"m\":{\"i\":400,\"s\":\"400\"}},{\"i\":5,\"s\":\"5\",\"m\":{\"i\":410,\"s\":\"410\"}},{\"i\":6,\"s\":\"6\",\"m\":{\"i\":420,\"s\":\"420\"}}]";
    stringstream ist(json);
    ist >> i;
    stringstream ou;
    ou << i;
    string r;
    ou >> r;
    CHECK(r==json);
}

TEST_CASE("json object from string"){
    struct Test_json_object: Json_object {
        Test_json_object(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                         })
    };
    Test_json_object tjo {1,"hello"};
    string json = "{\"i\":20,\"s\":\"bye\"}";
    json >> tjo;
    string r;
    r << tjo;
    CHECK(r==json);
    const Test_json_object tjo2{1,"hello"};
    stringstream o2;
    o2 << tjo2;
    string r2;
    o2 >> r2;
    CHECK(r2=="{\"i\":1,\"s\":\"hello\"}");
}

TEST_CASE("json object from char array"){
    struct Test_json_object: Json_object {
        Test_json_object(int i, string s): i(i), s(s) {}
        int i;
        string s;
        Json_object_members({
                             Add_member(i);
                             Add_member(s);
                         })
    };
    Test_json_object tjo {1,"hello"};
    "{\"i\":20,\"s\":\"bye\"}" >> tjo;
    string r;
    r << tjo;
    CHECK(r=="{\"i\":20,\"s\":\"bye\"}");
    const Test_json_object tjo2{1,"hello"};
    stringstream o2;
    o2 << tjo2;
    string r2;
    o2 >> r2;
    CHECK(r2=="{\"i\":1,\"s\":\"hello\"}");
}

TEST_CASE("fix pointer"){
    struct Test_object : Json_object{
        Test_object():Json_object(){}
        int a = 10,b = 20;
        Json_object_members({
            Add_member(a);
            Add_member(b);
        })
    };
    Test_object *t2 = new((Test_object *)malloc(sizeof(Test_object) + 4)) Test_object();
    stringstream o2;
    o2 << (*t2);
    CHECK(o2.str() == "{\"a\":10,\"b\":20}");
}

TEST_CASE("check needs quotes") {
    string a;
    int b;
    CHECK(needs_quotes<string>(a) == true);
    CHECK(needs_quotes<int>(b) == false);
    CHECK(Json_needs_quotes(a) == true);
    CHECK(Json_needs_quotes(b) == false);
}

TEST_CASE("dictionary") {
    string json = "{\"i\":20,\"s\":\"bye\",\"m\":{\"i\":200,\"s\":\"hello\"}}";
    stringstream ist(json);
    Json_dictionary dict;
    json >> dict;
    CHECK(dict.size() == 3);
    CHECK(dict.keys[0] == "i");
    CHECK(dict.keys[1] == "s");
    CHECK(dict.keys[2] == "m");
    CHECK(dict["i"].value=="20");
    CHECK(dict["s"].value=="bye");
    CHECK(dict["s"].require_quotes==true);
    CHECK(dict["m"].value=="{\"i\":200,\"s\":\"hello\"}");
    CHECK(dict["m"].to_dict()["i"].value=="200");
    CHECK(dict["m"].to_dict()["s"].value=="hello");
    CHECK(dict["m"].to_dict()["s"].require_quotes==true);
    CHECK(dict["m"].to_dict().keys[0] == "i");
    CHECK(dict["m"].to_dict().keys[1] == "s");
    stringstream ss;
    ss << dict;
    CHECK(ss.str()== "{\"i\":20,\"s\":\"bye\",\"m\":{\"i\":200,\"s\":\"hello\"}}");
    stringstream ss2;
    ss2 << dict["m"].to_dict();
    CHECK(ss2.str()== "{\"i\":200,\"s\":\"hello\"}");

}


TEST_CASE("json_util base64") {
    Json_buffer buffer;
    buffer.address = (void*) "any carnal pleasu";
    buffer.size = 18;
    stringstream ss;
    ss << "\"";
    Json_util::write_value(ss,buffer);
    ss << "\"";
    Json_buffer buffer1(true);
    Json_util::read_value(ss, buffer1);
    CHECK(strcmp((char*)buffer.address,(char*)buffer1.address) == 0);
    CHECK(buffer.size == buffer1.size);
}


struct Binary_test : Json_binary {
    virtual Json_buffer get_write_buffer() const override{
        return Json_buffer::new_buffer((void *)data.c_str(), data.size() + 1);
    };
    virtual void set_value(const Json_buffer &jb) override{
        data = (char *)jb.address;
    }
    string data;
};

TEST_CASE("json_util binary") {
    Binary_test bt;
    bt.data = "hello there!!!";

    stringstream ss;
    ss << bt;
    string sr = "\"" + ss.str() + "\"";
    CHECK(sr == "\"aGVsbG8gdGhlcmUhISEA\"");
    Binary_test bt1;
    sr >> bt1;
    CHECK (bt1.data == bt.data);
}

TEST_CASE("json_binary") {
    Binary_test bt;
    bt.data = "hello there!!!";

    stringstream ss;
    ss << bt;
    string sr = "\"" + ss.str() + "\"";
    CHECK(sr == "\"aGVsbG8gdGhlcmUhISEA\"");
    Binary_test bt1;
    sr >> bt1;
    CHECK (bt1.data == bt.data);
}

TEST_CASE("json_date") {
    Json_date::set_local_time_zone_offset();
    cout << "THIS SHOULD BE NOW " << Json_date::now() << endl;
    Json_date t;
    "\"2021-08-05 22:41:26.682\"" >> t;
    cout << t << endl;
}

struct Transformation : json_cpp::Json_object{
    double sIze{};
    double rotaTion{};
    Json_object_members({
                            Case_insensitive();
                            Add_member(sIze);
                            Add_member(rotaTion);
                        });
};

struct Location : json_cpp::Json_object {
    double x{}, y{};
    Json_object_members({
                            Add_member(x);
                            Add_member(y);
                        })
};

struct Location_list : json_cpp::Json_vector<Location> {
};


struct Shape : json_cpp::Json_object{
    int sides{};
    Json_object_members({
                            Add_member(sides);
                        })
};

struct Space : json_cpp::Json_object{
    enum Orientation{
        Flipped = -1,
        Not_flipped = 1
    };
    Location center;
    Shape shape;
    Transformation transformation;
    Json_object_members({
                            Add_member(center);
                            Add_member(shape);
                            Add_member(transformation);
                        })
};

struct World_implementation : json_cpp::Json_object{
    Location_list cell_locations;
    Space space;
    Transformation cell_transformation;
    Json_object_members({
                            Add_member(cell_locations);
                            Add_member(space);
                            Add_member(cell_transformation);
                        })
};


//
//TEST_CASE("world_implementation"){
//    string url ("https://raw.githubusercontent.com/germanespinosa/cellworld_data/master/world_implementation/hexagonal.vr.nonsense");
//    World_implementation wi;
//    cout << "sending the request" << endl;
//    Json_web_get(url, World_implementation);
//    cout << "response: " << wi << endl;
//}