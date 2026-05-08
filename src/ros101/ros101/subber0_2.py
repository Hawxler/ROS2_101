# 터틀봇의 위치 받기 기본 1 + timer
# Pub: 터틀심
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class TurtleSubber0_2(Node):
    def __init__(self):
        super().__init__('t_sub_node0_2')

        # 터틀심이 발행하는 pose 위치 정보 구독
        self.subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.sub_callback,
            10
        )
        self.subber # Prevent unused variable warning
        self.latest_pose = None

        self.timer = self.create_timer(0.5, self.timer_callback)

    # 터틀심이 보내주는 pose 정보 받기
    def sub_callback(self, msg):
        self.latest_pose = msg

    def timer_callback(self):
        if self.latest_pose is not None:
            self.get_logger().info(
                f'X: {self.latest_pose.x:.2f}, Y: {self.latest_pose.y:.2f}, Theta: {self.latest_pose.theta:.2f}'
            )
        else:
            print("아직 pose를 받지 못했습니다.")
    
def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleSubber0_2()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()