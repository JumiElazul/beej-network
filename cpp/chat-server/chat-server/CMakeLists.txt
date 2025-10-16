set(SERVER_SOURCES
    "src/main.cpp"
)

add_executable(chat-server ${SERVER_SOURCES})
target_link_libraries(chat-server PRIVATE project_options)
