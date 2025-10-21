#include "tcp_server.h"
#include <print>

tcp_server::tcp_server(asio::io_context& io_context, unsigned short port)
    : _context(io_context)
    , _acceptor(io_context, tcp::endpoint(tcp::v4(), port))
    , _port(port)
    , _active_connections() {
    std::println("Server listening on port {}...", _port);
    start_accept();
}

void tcp_server::start_accept() {
    tcp_connection::pointer new_conn = tcp_connection::create(_context);

    _acceptor.async_accept(new_conn->socket(), [this, new_conn](const asio::error_code& ec) {
        handle_connection_complete(new_conn, ec);
    });
}

void tcp_server::handle_connection_complete(tcp_connection::pointer new_connection,
                                            const std::error_code& error) {
    if (!error) {
        new_connection->start();

        // _active_connections.insert(new_connection);
        std::string addr = new_connection->socket().remote_endpoint().address().to_string();
        std::println("New connection address {} added to active connections (total active: {})",
                     addr, _active_connections.size());
    }

    start_accept();
}
