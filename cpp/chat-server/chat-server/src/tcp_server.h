#ifndef JUMI_CHAT_SERVER_TCP_SERVER_H
#define JUMI_CHAT_SERVER_TCP_SERVER_H
#include "tcp_connection.h"
#include <asio.hpp>
#include <set>

using asio::ip::tcp;

class tcp_server {
public:
    tcp_server(asio::io_context& io_context, unsigned short port);

private:
    asio::io_context& _context;
    tcp::acceptor _acceptor;
    unsigned short _port;

    std::set<tcp_connection::pointer> _active_connections;

    void start_accept();
    void handle_connection_complete(tcp_connection::pointer new_connection,
                                    const std::error_code& error);
};

#endif
