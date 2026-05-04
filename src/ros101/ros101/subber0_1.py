# 터틀봇의 위치 받기 기본 1
# Pub: 터틀심
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtleSubber0_1(Node):
    def __init__(self):
        super().__init__('t_sub_node0_1')
        self.subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.callback,
            10
        )
        self.subber # Prevent unused variable warning
    def callback(self, msg):
        print("X:", msg.x, ", Y:", msg.y)
        # 터틀 퍼블리셔가 보내는 msg: publish(msg)
        # msg = Twist()
        # msg.linear.x = 1.0
        # msg.angular.z = 0.5
        # msg.pubber.publish(msg) 
        # 즉, 위 linear, angular 값이 담긴 Twist 객체 하나를 퍼블리시함.

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleSubber0_1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()