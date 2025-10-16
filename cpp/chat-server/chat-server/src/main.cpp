#include <asio.hpp>
#include <ctime>
#include <iostream>
#include <string>

std::string make_daytime_string() {
    using namespace std;
    time_t now = time(0);
    return ctime(&now);
}

class validated_port {
public:
    explicit validated_port(const std::string& port_str) {
        long temp = 0;
        auto begin = port_str.data();
        auto end = port_str.data() + port_str.size();
        auto result = std::from_chars(begin, end, temp);

        if (result.ec != std::errc{} || result.ptr != end) {
            throw std::invalid_argument("Port string is not a valid integer: '" + port_str + "'");
        }

        if (temp < 1025 || temp > static_cast<long>(std::numeric_limits<unsigned short>::max())) {
            throw std::out_of_range("Port specified was out of range: " + port_str);
        }

        _port = static_cast<unsigned short>(temp);
    }

    operator asio::ip::port_type() const noexcept { return _port; }

private:
    unsigned short _port = 0;
};

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: chat-server <port>\n";
        std::exit(1);
    }

    try {
        std::string port_str = argv[1];
        validated_port port = validated_port(port_str);

        asio::io_context io_context;

        asio::ip::tcp::acceptor acceptor(io_context,
                                         asio::ip::tcp::endpoint(asio::ip::tcp::v4(), port));

        std::cout << "chat-server listening on port " << port << "...\n";

        while (true) {
            asio::ip::tcp::socket socket(io_context);
            acceptor.accept(socket);

            std::string message = make_daytime_string();

            std::error_code ignored_error;
            asio::write(socket, asio::buffer(message), ignored_error);
        }
    } catch (std::exception& e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}
