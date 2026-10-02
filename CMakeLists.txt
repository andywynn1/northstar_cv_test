cmake_minimum_required(VERSION 3.16)

project(auto_aim LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# External dependencies
find_package(OpenCV REQUIRED)
find_package(OpenVINO REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(fmt REQUIRED)

add_executable(usbcamera_detect_test
    tests/usbcamera_detect_test.cpp

    io/usbcamera/usbcamera.cpp

    tasks/auto_aim/armor.cpp
    tasks/auto_aim/yolo.cpp
    tasks/auto_aim/yolos/yolov5.cpp

    tools/exiter.cpp
    tools/img_tools.cpp
    tools/logger.cpp
    tools/math_tools.cpp
)

# Allows includes such as:
# #include "tools/logger.hpp"
# #include "tasks/auto_aim/yolo.hpp"
target_include_directories(usbcamera_detect_test PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(usbcamera_detect_test PRIVATE
    ${OpenCV_LIBS}
    openvino::runtime
    yaml-cpp
    fmt::fmt
)
