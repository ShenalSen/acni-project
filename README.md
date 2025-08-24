# ACNI Project - Adaptive Video Streaming

## PUSL3130 - Advanced Computing and Networking Infrastructures

This project implements an adaptive video streaming testbed using DASH.js, Mininet, and SDN controllers to investigate how network conditions affect video streaming quality.

## Project Structure

- `servers/` - Nginx configuration and video content
- `mininet/` - Network topology and test scripts  
- `sdn-controller/` - Ryu SDN application for traffic management
- `experiments/` - Test results and analysis
- `docs/` - Project documentation and demo video

## Quick Start

1. **Activate virtual environment:**
   ```bash
   source ../acni-project/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   sudo apt install nginx mininet ffmpeg mp4box
   pip install ryu
   ```

3. **Start Ryu controller:**
   ```bash
   ryu-manager sdn-controller/ryu-app.py
   ```

4. **Run Mininet topology:**
   ```bash
   sudo python3 mininet/topology.py
   ```

## Video Processing

1. Download Big Buck Bunny sample video
2. Use MP4Box to create DASH segments:
   ```bash
   MP4Box -dash 4000 -frag 4000 -rap -segment-name 'segment_' input.mp4
   ```

## Experiments

Run network tests with varying conditions:
- Low bandwidth (1 Mbps)
- Medium bandwidth (5 Mbps) 
- High bandwidth (10 Mbps)
- High traffic load scenarios
- Edge vs central server comparison

## Results Analysis

Measure and analyze:
- Latency and bandwidth utilization
- DASH.js statistics (bitrate, dropped frames)
- Impact of traffic redirection
- Edge computing effectiveness

## Author

Student Name - PUSL3130 Coursework
