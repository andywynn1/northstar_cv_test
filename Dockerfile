FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake curl ca-certificates \
    libopencv-dev libfmt-dev libeigen3-dev libspdlog-dev libyaml-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# OpenVINO 2024.6 (same version sp_vision_25 uses)
RUN mkdir -p /opt/intel \
    && curl -L https://storage.openvinotoolkit.org/repositories/openvino/packages/2024.6/linux/l_openvino_toolkit_ubuntu22_2024.6.0.17404.4c0f47d2335_x86_64.tgz -o /tmp/ov.tgz \
    && tar -xf /tmp/ov.tgz -C /tmp \
    && mv /tmp/l_openvino_toolkit_ubuntu22_2024.6.0.17404.4c0f47d2335_x86_64 /opt/intel/openvino_2024.6.0 \
    && rm /tmp/ov.tgz \
    && /opt/intel/openvino_2024.6.0/install_dependencies/install_openvino_dependencies.sh -y \
    && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/opt/intel/openvino_2024.6.0/runtime/lib/intel64:/opt/intel/openvino_2024.6.0/runtime/3rdparty/tbb/lib

WORKDIR /app
COPY . .
RUN cmake -B build -DOpenVINO_DIR=/opt/intel/openvino_2024.6.0/runtime/cmake \
    && cmake --build build -j

ENTRYPOINT ["./build/camera_demo"]
CMD ["configs/default.yaml", "0"]
