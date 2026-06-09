# [sdf 연습] ws_gz1 > robot1.sdf 세계를 Gazebo에서 구동하기
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class GazeboCmdPub1(Node):
    def __init__(self):
        super().__init__('gz_pub_node1')

        self.pubber = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.timer_period = 0.1
        self.timer = self.create_timer(
            self.timer_period,
            self.timer_callback
        )

        self.count = 0
        self.get_logger().info('Gazebo /cmd_vel 발행 시작')
    
    def timer_callback(self):
        msg = Twist()

        # 0~4초 전진
        if self.count < 40:
            msg.linear.x = 0.5
            msg.angular.z = 0.0
        
        # 4~7초 좌회전
        elif self.count < 70:
            msg.linear.x = 0.0
            msg.angular.z = 0.5

        # 7~11초 후진
        elif self.count < 110:
            msg.linear.x = -0.5
            msg.angular.z = 0.0
        
        # 11~70초 원 그리기
        elif self.count < 700:
            msg.linear.x = 2.0
            msg.angular.z = 1.0

        # 70초 후 정지
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.pubber.publish(msg)

        self.get_logger().info(
            f'[/cmd_vel 발행] linear.x={msg.linear.x:.2f}'
            f'angular.z={msg.angular.z:.2f}'
        )

        self.count += 1

    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.pubber.publish(msg)
        self.get_logger().info("로봇 정지 명령 발행")

def main(args=None):
    rclpy.init(args=args)

    node1 = GazeboCmdPub1()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info('Ctrl+C 입력됨')
    finally:
        node1.stop_robot()
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()