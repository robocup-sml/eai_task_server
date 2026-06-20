#!/usr/bin/env python3

from typing import Callable, Dict, Tuple

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from sml_messages.msg import Order, Station, Task


TaskBuilder = Callable[[], Task]


def make_order(order_type: int, name: str, product_id: int) -> Order:
    order = Order()
    order.order_type = order_type
    order.name = name
    order.product_id = product_id
    return order


def make_station(station_type: int, name: str, station_id: int, material_ids: list[int]) -> Station:
    station = Station()
    station.station_type = station_type
    station.name = name
    station.station_id = station_id
    station.material_ids = material_ids
    return station


def build_production_beginner_task() -> Task:
    task = Task()
    task.order_list = [
        make_order(Order.OT_PRODUCE, 'pb_order_1', 1),
        make_order(Order.OT_PRODUCE, 'pb_order_2', 2),
    ]
    task.arena_layout = [
        make_station(Station.ST_STORAGE, 'storage_a', 1, [1, 2, 3]),
        make_station(Station.ST_WORKBENCH, 'workbench_a', 2, []),
        make_station(Station.ST_CUSTOMER, 'customer_a', 3, []),
    ]
    return task


def build_production_advanced_task() -> Task:
    task = Task()
    task.order_list = [
        make_order(Order.OT_PRODUCE, 'pa_order_1', 3),
        make_order(Order.OT_PRODUCE, 'pa_order_2', 4),
        make_order(Order.OT_PRODUCE, 'pa_order_3', 5),
    ]
    task.arena_layout = [
        make_station(Station.ST_STORAGE, 'storage_a', 1, [1, 2, 3, 4]),
        make_station(Station.ST_STORAGE, 'storage_b', 2, [5, 6]),
        make_station(Station.ST_WORKBENCH, 'workbench_a', 3, []),
        make_station(Station.ST_HYBRID, 'hybrid_a', 4, []),
        make_station(Station.ST_CUSTOMER, 'customer_a', 5, []),
    ]
    return task


def build_recycling_beginner_task() -> Task:
    task = Task()
    task.order_list = [
        make_order(Order.OT_RECYCLE, 'rb_order_1', 1),
        make_order(Order.OT_RECYCLE, 'rb_order_2', 2),
    ]
    task.arena_layout = [
        make_station(Station.ST_CUSTOMER, 'collection_a', 1, []),
        make_station(Station.ST_WORKBENCH, 'sort_a', 2, []),
        make_station(Station.ST_STORAGE, 'storage_a', 3, [1, 2, 3]),
    ]
    return task


def build_recycling_advanced_task() -> Task:
    task = Task()
    task.order_list = [
        make_order(Order.OT_RECYCLE, 'ra_order_1', 3),
        make_order(Order.OT_RECYCLE, 'ra_order_2', 4),
        make_order(Order.OT_RECYCLE, 'ra_order_3', 5),
    ]
    task.arena_layout = [
        make_station(Station.ST_CUSTOMER, 'collection_a', 1, []),
        make_station(Station.ST_CUSTOMER, 'collection_b', 2, []),
        make_station(Station.ST_WORKBENCH, 'sort_a', 3, []),
        make_station(Station.ST_HYBRID, 'hybrid_a', 4, []),
        make_station(Station.ST_STORAGE, 'storage_a', 5, [1, 2, 3, 4, 5, 6]),
    ]
    return task


def build_lifecycle_beginner_task() -> Task:
    task = Task()
    task.order_list = [
        make_order(Order.OT_PRODUCE, 'lb_prod_1', 1),
        make_order(Order.OT_RECYCLE, 'lb_recycle_1', 1),
    ]
    task.arena_layout = [
        make_station(Station.ST_STORAGE, 'storage_a', 1, [1, 2]),
        make_station(Station.ST_WORKBENCH, 'workbench_a', 2, []),
        make_station(Station.ST_CUSTOMER, 'customer_a', 3, []),
    ]
    return task


def build_lifecycle_advanced_task() -> Task:
    task = Task()
    task.order_list = [
        make_order(Order.OT_PRODUCE, 'la_prod_1', 2),
        make_order(Order.OT_PRODUCE, 'la_prod_2', 3),
        make_order(Order.OT_RECYCLE, 'la_recycle_1', 2),
        make_order(Order.OT_RECYCLE, 'la_recycle_2', 4),
    ]
    task.arena_layout = [
        make_station(Station.ST_STORAGE, 'storage_a', 1, [1, 2, 3, 4]),
        make_station(Station.ST_WORKBENCH, 'workbench_a', 2, []),
        make_station(Station.ST_HYBRID, 'hybrid_a', 3, []),
        make_station(Station.ST_CUSTOMER, 'customer_a', 4, []),
        make_station(Station.ST_CUSTOMER, 'customer_b', 5, []),
    ]
    return task


TASK_BUILDERS: Dict[Tuple[str, str], TaskBuilder] = {
    ('production', 'beginner'): build_production_beginner_task,
    ('production', 'advanced'): build_production_advanced_task,
    ('recycling', 'beginner'): build_recycling_beginner_task,
    ('recycling', 'advanced'): build_recycling_advanced_task,
    ('lifecycle', 'beginner'): build_lifecycle_beginner_task,
    ('lifecycle', 'advanced'): build_lifecycle_advanced_task,
}


class TaskPublisherNode(Node):
    def __init__(self) -> None:
        super().__init__('task_publisher')

        self.declare_parameter('scenario', 'production')
        self.declare_parameter('stage', 'beginner')
        self.declare_parameter('topic_name', '/eai/task')
        self.declare_parameter('publish_period_sec', 1.0)
        self.declare_parameter('publish_once', False)

        scenario = self.get_parameter('scenario').get_parameter_value().string_value.strip().lower()
        stage = self.get_parameter('stage').get_parameter_value().string_value.strip().lower()
        topic_name = self.get_parameter('topic_name').get_parameter_value().string_value
        period = self.get_parameter('publish_period_sec').get_parameter_value().double_value
        publish_once = self.get_parameter('publish_once').get_parameter_value().bool_value

        key = (scenario, stage)
        if key not in TASK_BUILDERS:
            valid = ', '.join([f'{k[0]}/{k[1]}' for k in TASK_BUILDERS.keys()])
            raise ValueError(f'Unsupported scenario/stage: {scenario}/{stage}. Valid options: {valid}')

        self._build_task = TASK_BUILDERS[key]
        self._publish_once = publish_once
        self._publisher = self.create_publisher(Task, topic_name, 10)
        self._timer = self.create_timer(period, self._publish_task)

        self.get_logger().info(
            f'Publishing task on {topic_name} for scenario={scenario}, stage={stage} every {period:.2f}s '
            f'(publish_once={publish_once})'
        )

    def _publish_task(self) -> None:
        task = self._build_task()
        self._publisher.publish(task)
        self.get_logger().debug(
            f'Published task with {len(task.order_list)} orders and {len(task.arena_layout)} stations'
        )

        if self._publish_once:
            self.get_logger().info('Published one task. Shutting down.')
            self._timer.cancel()
            if rclpy.ok():
                rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TaskPublisherNode()

    try:
        rclpy.spin(node)
    except ExternalShutdownException:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
