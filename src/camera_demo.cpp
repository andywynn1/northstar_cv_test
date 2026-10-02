#include <fmt/core.h>

#include <algorithm>
#include <cctype>
#include <chrono>
#include <filesystem>
#include <opencv2/opencv.hpp>
#include <string>

#include "tasks/auto_aim/yolo.hpp"
#include "tools/img_tools.hpp"
#include "tools/logger.hpp"

// usage: camera_demo [config.yaml] [camera index, video file, or http URL] [--headless]
int main(int argc, char * argv[])
{
  std::filesystem::create_directories("logs");  // the logger writes here
  std::filesystem::create_directories("out");   // headless snapshots go here

  std::string config_path = argc > 1 ? argv[1] : "configs/default.yaml";
  std::string source = argc > 2 ? argv[2] : "0";
  bool headless = argc > 3 && std::string(argv[3]) == "--headless";

  bool is_index = !source.empty() && std::all_of(source.begin(), source.end(), [](unsigned char c) {
                    return std::isdigit(c);
                  });
  cv::VideoCapture cap;
  if (is_index) cap.open(std::stoi(source));
  else cap.open(source);

  if (!cap.isOpened()) {
    tools::logger()->error("Cannot open source: {}", source);
    return 1;
  }

  auto_aim::YOLO yolo(config_path, !headless);  // debug=true shows the "detection" window

  cv::Mat frame;
  int frame_count = 0;
  auto last = std::chrono::steady_clock::now();

  while (true) {
    cap >> frame;
    if (frame.empty()) break;

    auto armors = yolo.detect(frame, frame_count++);

    auto now = std::chrono::steady_clock::now();
    double dt = std::chrono::duration<double>(now - last).count();
    last = now;
    tools::logger()->info("{} armors, {:.1f} fps", armors.size(), 1.0 / dt);

    if (headless) {
      if (frame_count % 15 == 0) {
        cv::Mat vis = frame.clone();
        for (const auto & a : armors) {
          tools::draw_points(vis, a.points, {0, 255, 0});
          tools::draw_text(
            vis, fmt::format("{} {:.2f}", auto_aim::ARMOR_NAMES[a.name], a.confidence), a.center,
            {0, 255, 0});
        }
        cv::imwrite("out/latest.jpg", vis);
      }
    } else if (cv::waitKey(1) == 'q') {
      break;
    }
  }
  return 0;
}
