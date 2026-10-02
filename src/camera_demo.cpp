#include <algorithm>
#include <chrono>
#include <opencv2/opencv.hpp>
#include <string>

#include "tasks/auto_aim/yolo.hpp"
#include "tools/logger.hpp"

// usage: camera_demo [config.yaml] [camera index or video file]
int main(int argc, char * argv[])
{
  std::string config_path = argc > 1 ? argv[1] : "configs/default.yaml";
  std::string source = argc > 2 ? argv[2] : "0";

  bool is_index = std::all_of(source.begin(), source.end(), ::isdigit);
  cv::VideoCapture cap;
  if (is_index) cap.open(std::stoi(source));
  else cap.open(source);

  if (!cap.isOpened()) {
    tools::logger()->error("Cannot open source: {}", source);
    return 1;
  }

  auto_aim::YOLO yolo(config_path, true);  // true shows the "detection" window

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

    if (cv::waitKey(1) == 'q') break;
  }
  return 0;
}
