#include <array>
#include <asio.hpp>
#include <iostream>

using asio::ip::tcp;

static constexpr size_t MAX_MESSAGE_SIZE = 1024;

int main(int argc, char* argv[]) {
    try {
        if (argc != 3) {
            std::cerr << "usage: chat-client <host> <port>\n";
            return 1;
        }

        asio::io_context io_context;

        tcp::resolver resolver(io_context);
        tcp::resolver::results_type endpoints = resolver.resolve(argv[1], argv[2]);

        tcp::socket socket(io_context);
        asio::connect(socket, endpoints);

        while (true) {
            std::array<char, MAX_MESSAGE_SIZE> buf;
            std::error_code error;

            size_t len = socket.read_some(asio::buffer(buf), error);

            if (error == asio::error::eof)
                break;
            else if (error)
                throw asio::system_error(error);

            std::cout.write(buf.data(), static_cast<std::streamsize>(len));

            std::string line;
            std::getline(std::cin, line);
            asio::write(socket, asio::buffer(line));
        }
    } catch (std::exception& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
