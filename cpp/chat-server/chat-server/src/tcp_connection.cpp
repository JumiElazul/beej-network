#include "tcp_connection.h"
#include <print>

tcp_connection::tcp_connection(asio::io_context& io_context)
    : _socket(io_context) {}

tcp_connection::pointer tcp_connection::create(asio::io_context& io_context) {
    return pointer(new tcp_connection(io_context));
}

void tcp_connection::start() { handle_write(_entry_message); }

void tcp_connection::begin_listen_loop() {
    _socket.async_read_some(
        asio::buffer(_read_buffer),
        [self = shared_from_this()](const asio::error_code& ec, std::size_t bytes_transferred) {
            self->handle_read(ec, bytes_transferred);
        });
}

void tcp_connection::handle_read(const asio::error_code& err_code, std::size_t bytes_transferred) {
    if (err_code) {
        std::println(stderr, "Error on async_read_some: {}", err_code.message());
        return;
    }

    std::string received(_read_buffer.data(), bytes_transferred);
    handle_write(received);
}

void tcp_connection::handle_write(const std::string& message) {
    std::copy_n(message.begin(), message.size(), _write_buffer.begin());
    std::copy_n("\n", 1, _write_buffer.begin() + message.size());

    asio::async_write(
        _socket, asio::buffer(_write_buffer),
        [self = shared_from_this()](const asio::error_code& err_code, size_t bytes_transferred) {
            self->handle_write_complete(err_code, bytes_transferred);
        });
}

void tcp_connection::handle_write_complete(const asio::error_code& err_code,
                                           size_t bytes_transferred) {
    if (err_code) {
        std::println(stderr, "Error on async_write: {}", err_code.message());
        return;
    }

    begin_listen_loop();
}
