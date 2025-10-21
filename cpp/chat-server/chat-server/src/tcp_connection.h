#ifndef JUMI_CHAT_SERVER_TCP_CONNECTION_H
#define JUMI_CHAT_SERVER_TCP_CONNECTION_H
#include "common.h"
#include <array>
#include <asio.hpp>
#include <memory>
#include <string>

using asio::ip::tcp;

class tcp_connection : public std::enable_shared_from_this<tcp_connection> {
public:
    using pointer = std::shared_ptr<tcp_connection>;

    static pointer create(asio::io_context& io_context);
    tcp::socket& socket() { return _socket; }
    void start();

private:
    tcp::socket _socket;
    std::string _entry_message = "Connected to Server.";

    std::array<char, 32> _read_buffer{};
    std::array<char, 32> _write_buffer{};

    tcp_connection(asio::io_context& io_context);

    void begin_listen_loop();
    void handle_read(const asio::error_code& err_code, std::size_t bytes_transferred);
    void handle_read_complete(const asio::error_code& err_code, std::size_t bytes_transferred);
    void handle_write(const std::string& message);
    void handle_write_complete(const asio::error_code& err_code, size_t bytes_transferred);
};

#endif
