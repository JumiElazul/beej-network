set(SERVER_SOURCES
    "src/main.cpp"
    "src/common.h"

    "src/tcp_connection.cpp"
    "src/tcp_connection.h"
    "src/tcp_server.cpp"
    "src/tcp_server.h"
)

add_executable(chat-server ${SERVER_SOURCES})
target_link_libraries(chat-server PRIVATE project_options)
