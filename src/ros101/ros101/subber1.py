# pubber1.py의 터틀 cmd_vel 받아 출력
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleSubber1(Node):
    def __init__(self):
        super().__init__('t_sub_node1')
        self.subber = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.subcallback,
            10
        )
        self.subber
    
    def subcallback(self, msg):
        self.get_logger().info(f'[Subber heard] X: {msg.linear.x}, Y: {msg.angular.z}')
    
def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleSubber1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()