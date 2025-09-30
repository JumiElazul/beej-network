#include <arpa/inet.h>
#include <atomic>
#include <csignal>
#include <cstring>
#include <print>
#include <semaphore>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>

#define MAX_PENDING_CONNECTIONS 128

static std::atomic<bool> server_running = true;

class destructable_socket {
public:
    destructable_socket(int sockfd)
        : _sockfd(sockfd) {
        std::println("Opening socket on fd {}", _sockfd);
    }

    ~destructable_socket() {
        std::println("Closing socket on fd {}", _sockfd);
        close(_sockfd);
    }
    destructable_socket(const destructable_socket&) = delete;
    destructable_socket& operator=(const destructable_socket&) = delete;
    destructable_socket(destructable_socket&& rhs)
        : _sockfd(std::exchange(rhs._sockfd, -1)) {}

    destructable_socket& operator=(destructable_socket&& rhs) {
        if (this != &rhs) {
            _sockfd = std::exchange(rhs._sockfd, -1);
        }
        return *this;
    }

    [[nodiscard]] int sockfd() const noexcept { return _sockfd; }

private:
    int _sockfd = -1;
};

void sigint_handler(int signum) {
    std::println("SIGINT received, stopping server.");
    server_running.store(false, std::memory_order_relaxed);
}

void bind_sigint() {
    struct sigaction sa {};
    sa.sa_handler = sigint_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    if (sigaction(SIGINT, &sa, nullptr) < 0) {
        perror("Error setting up signal handler");
        std::exit(1);
    }
}

int main() {
    bind_sigint();
    static uint16_t target_port = 21055;

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket()");
        std::exit(1);
    }

    destructable_socket serv_sock = destructable_socket(sockfd);

    int optval;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0) {
        perror("setsockopt()");
        std::exit(1);
    }

    struct sockaddr_in server_addr;
    std::memset(&server_addr, 0, sizeof(sockaddr_in));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(target_port);

    if (bind(serv_sock.sockfd(), reinterpret_cast<const struct sockaddr*>(&server_addr),
             sizeof(server_addr)) < 0) {
        perror("bind()");
        std::exit(1);
    }

    if (listen(serv_sock.sockfd(), MAX_PENDING_CONNECTIONS) < 0) {
        perror("listen");
        std::exit(1);
    }

    std::println("Webserver listening on port {}...", target_port);

    while (server_running) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_sockfd = accept(serv_sock.sockfd(), (struct sockaddr*)&client_addr, &client_len);
        if (client_sockfd < 0) {
            perror("accept");
            continue;
        }

        destructable_socket client_sock = destructable_socket(client_sockfd);
        char buf[128];
        if (recv(client_sock.sockfd(), &buf, 128, 0) < 0) {
            perror("recv");
            continue;
        }

        std::println("{}", buf);
    }
}
