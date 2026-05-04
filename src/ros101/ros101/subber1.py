# 터틀봇의 위치 받기 기본 1
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtleSubber1(Node):
    def __init__(self):
        super().__init__('t_sub_node1')
        self.subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.callback,
            10
        )
        self.subber # Prevent unused variable warning
    def callback(self, msg):
        print("X:", msg.x, ", Y:", msg.y)

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleSubber1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()