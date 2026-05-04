# 터틀심을 cmd_vel로 조종하고 서브스크라이버(subber1)에게 명령 메시지(Twist()의 linear.x, angular.z) 전송
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtlePubber1(Node):
    def __init__(self):
        super().__init__('t_pub_node1')
        self.pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0
        self.pubber.publish(msg)
        self.get_logger().info(f'[from Pubber] linear={msg.linear.x}, angular={msg.angular.z}')

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtlePubber1()
    rclpy.spin(node1)
    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()
