#include <asio.hpp>
#include <ctime>
#include <print>
#include <set>

using asio::ip::tcp;

std::string make_daytime_string() {
    using namespace std;
    time_t now = time(0);
    return ctime(&now);
}

class tcp_connection : public std::enable_shared_from_this<tcp_connection> {
public:
    using pointer = std::shared_ptr<tcp_connection>;

    static pointer create(asio::io_context& io_context) {
        return pointer(new tcp_connection(io_context));
    }

    tcp::socket& socket() { return _socket; }

    void start() {
        _message = make_daytime_string();

        asio::async_write(_socket, asio::buffer(_message),
                          [self = shared_from_this()](const asio::error_code& err_code,
                                                      size_t bytes_transferred) {
                              self->handle_write_completion(err_code, bytes_transferred);
                          });
    }

private:
    tcp::socket _socket;
    std::string _message;

    tcp_connection(asio::io_context& io_context)
        : _socket(io_context) {}

    void handle_write_completion(const asio::error_code& err_code, size_t bytes_transferred) {
        if (err_code) {
            std::println(stderr, "Error on async_write: {}", err_code.message());
            return;
        }
    }
};

class tcp_server {
public:
    tcp_server(asio::io_context& io_context, unsigned short port)
        : _context(io_context)
        , _acceptor(io_context, tcp::endpoint(tcp::v4(), port))
        , _port(port)
        , _active_connections() {
        std::println("Server listening on port {}...", _port);
        start_accept();
    }

private:
    asio::io_context& _context;
    tcp::acceptor _acceptor;
    unsigned short _port;

    std::set<tcp_connection::pointer> _active_connections;

    void start_accept() {
        tcp_connection::pointer new_conn = tcp_connection::create(_context);

        _acceptor.async_accept(new_conn->socket(), [this, new_conn](const asio::error_code& ec) {
            handle_new_connection_completion(new_conn, ec);
        });
    }

    void handle_new_connection_completion(tcp_connection::pointer new_connection,
                                          const std::error_code& error) {
        if (!error) {
            new_connection->start();
        }

        // _active_connections.insert(new_connection);
        // std::string addr = new_connection->socket().remote_endpoint().address().to_string();
        // std::println("New connection address {} added to active connections (total active: {})",
        //              addr, _active_connections.size());
        start_accept();
    }
};

int main(int argc, char** argv) {
    try {
        unsigned short port = 12345;

        if (argc >= 2) {
            port = static_cast<unsigned short>(std::stoi(argv[1]));
        }

        asio::io_context io_context;
        tcp_server server(io_context, port);
        io_context.run();
    } catch (std::exception& e) {
        std::println(stderr, "{}", e.what());
    }

    return 0;
}
