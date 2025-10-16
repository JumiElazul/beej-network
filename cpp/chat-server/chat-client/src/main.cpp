#include <array>
#include <asio.hpp>
#include <iostream>

int main(int argc, char** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: chat-client <host> <port>\n";
            std::exit(1);
        }

        asio::io_context io_ctx;
        asio::ip::tcp::resolver resolver(io_ctx);
        asio::ip::tcp::resolver::results_type endpoints = resolver.resolve(argv[1], argv[2]);

        asio::ip::tcp::socket socket(io_ctx);
        asio::connect(socket, endpoints);

        while (true) {
            std::array<char, 128> buf;
            std::error_code error;

            size_t len = socket.read_some(asio::buffer(buf), error);
            if (error == asio::error::eof) {
                break;
            } else if (error) {
                throw std::system_error(error);
            }

            std::cout.write(buf.data(), (long)len);

            if (std::cout.bad()) {
                std::cerr << "Badbit was set\n";
                throw std::system_error(error);
            }
        }
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
    }
}
