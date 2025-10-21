#include "tcp_server.h"
#include <asio.hpp>
#include <cstring>
#include <ctime>
#include <print>

using asio::ip::tcp;

// void signal_handler(asio::error_code err_code, int signal) {
//     // sigdescr_np works on Windows?
//     const char* signal_str = sigdescr_np(signal);
//     std::println("signal_handler - errcode: {}   signal: {}", err_code.message(), signal_str);
// }

int main(int argc, char** argv) {
    try {
        unsigned short port = 12345;

        if (argc >= 2) {
            port = static_cast<unsigned short>(std::stoi(argv[1]));
        }

        asio::io_context io_context;
        // asio::signal_set signals(io_context, SIGINT);
        // signals.async_wait(signal_handler);

        tcp_server server(io_context, port);
        io_context.run();
    } catch (std::exception& e) {
        std::println(stderr, "{}", e.what());
    }

    return 0;
}
