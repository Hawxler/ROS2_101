# 커스텀 메시지 타입의 토픽 2개 구독하기
# 1단계: 그냥 Pose 1개 받기, 
# 2단계(sub_msg2.py): cmd_vel도 받기
# https://www.notion.so/M-1c1a5c22d8918090be1acb4d45fb9e91?source=copy_link#1c1a5c22d891807b8acce00fbad5a616
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

from interface_pkg1.msg import MyMessage1

class MsgSubber1(Node):
    def __init__(self):
        super().__init__("turtle_msg1")
        self.subber1 = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.listener_callback,
            10
        )
        self.cmd_pose = MyMessage1()
        
    def listener_callback(self, msg):
        self.get_logger().info(f"Turtle1: x={msg.x}, y={msg.y}, theta={msg.theta}")

        self.cmd_pose.pose_x = msg.x
        self.cmd_pose.pose_y = msg.y
        self.cmd_pose.linear_vel = msg.linear_velocity
        self.cmd_pose.angular_vel=msg.angular_velocity
        print(self.cmd_pose)

def main(args=None):
    rclpy.init(args=args)

    node1 = MsgSubber1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()