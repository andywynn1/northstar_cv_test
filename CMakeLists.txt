cmake_minimum_required(VERSION 3.16)
project(northstar_cv_test)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

find_package(OpenCV REQUIRED)
find_package(fmt REQUIRED)
find_package(spdlog REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(OpenVINO REQUIRED COMPONENTS Runtime)

include_directories(${PROJECT_SOURCE_DIR} ${OpenCV_INCLUDE_DIRS})

add_library(tools STATIC tools/img_tools.cpp tools/logger.cpp)
target_link_libraries(tools PUBLIC ${OpenCV_LIBS} fmt::fmt spdlog::spdlog)

add_library(auto_aim STATIC
  tasks/auto_aim/armor.cpp
  tasks/auto_aim/yolo.cpp
  tasks/auto_aim/yolos/yolov5.cpp)
target_link_libraries(auto_aim PUBLIC tools Eigen3::Eigen yaml-cpp openvino::runtime)

add_executable(camera_demo src/camera_demo.cpp)
target_link_libraries(camera_demo PRIVATE auto_aim)
