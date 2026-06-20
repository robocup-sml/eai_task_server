# eai_task_server

ROS 2 Python package that publishes hardcoded EAI task messages.

## Run

```bash
source /opt/ros/humble/setup.bash
source /home/marco/ros2_ws/install/setup.bash
ros2 run eai_task_server task_publisher --ros-args -p scenario:=production -p stage:=beginner
```

In a second terminal, run:

```bash
source /opt/ros/humble/setup.bash
source /home/marco/ros2_ws/install/setup.bash
ros2 run eai_task_server task_listener
```

## Parameters

- `scenario`: `production`, `recycling`, or `lifecycle`
- `stage`: `entry`, `beginner`, or `advanced`
- `topic_name`: publish topic (default `/eai/task`)
- `publish_period_sec`: publish period in seconds (default `1.0`)
- `publish_once`: publish a single message and exit (default `false`)

## Launch Server

```bash
source /opt/ros/humble/setup.bash
source /home/marco/ros2_ws/install/setup.bash
ros2 launch eai_task_server task_server.launch.py scenario:=lifecycle stage:=advanced
```

One-shot launch example:

```bash
ros2 launch eai_task_server task_server.launch.py scenario:=production stage:=beginner publish_once:=true
```

## Launch Server + Listener

```bash
source /opt/ros/humble/setup.bash
source /home/marco/ros2_ws/install/setup.bash
ros2 launch eai_task_server task_server_with_listener.launch.py scenario:=recycling stage:=advanced
```

Combined one-shot example:

```bash
ros2 launch eai_task_server task_server_with_listener.launch.py scenario:=production stage:=beginner publish_once:=true
```
