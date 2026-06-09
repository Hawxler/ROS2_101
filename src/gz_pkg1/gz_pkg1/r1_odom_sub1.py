# Gazebo robot1으로부터 odom 구독하여 출력하기
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class GazeboOdomSub(Node):
    def __init__(self):
        super().__init__('gz_sub_node1')

        self.subber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.count = 0
        self.get_logger().info("Gazebo /odom 구독 시작")

    def odom_callback(self, msg):
        # 너무 빨리 출력되지 않도록 10번에 1번만 출력
        self.count += 1

        if self.count % 10 != 0:
            return
        
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z

        vx = msg.twist.twist.linear.x
        wz = msg.twist.twist.angular.z

        self.get_logger().info(
            f'odom 위치: x={x:.2f}, y={y:.2f}, z={z:.2f} | '
            f'속도: linear.x={vx:.2f}, angular.z={wz:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)

    node1 = GazeboOdomSub()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info("Ctrl+C 입력됨")
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()