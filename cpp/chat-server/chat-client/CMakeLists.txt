set(CLIENT_SOURCES
    "src/main.cpp"
)

add_executable(chat-client ${CLIENT_SOURCES})
target_link_libraries(chat-client PRIVATE project_options)
