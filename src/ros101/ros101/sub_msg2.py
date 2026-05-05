# 커스텀 메시지 타입의 토픽 2개 구독하기
# pose, cmd_vel 두 개 받기
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from interface_pkg1.msg import MyMessage1

class MsgSubber2(Node):
    def __init__(self):
        super().__init__('turtle_msg2')

        self.subber_pose = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.subber_cmd_vel = self.create_subscription(
            Twist,
            '/turtle1/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.last_cmd_vel_linear = 0.0
        self.last_cmd_vel_angular = 0.0

    def cmd_vel_callback(self, msg):
        self.last_cmd_vel_linear = msg.linear.x
        self.last_cmd_vel_angular = msg.angular.z
    
    def pose_callback(self, msg):
        cmd_pose = MyMessage1()

        # /turtle1/cmd_vel에서 받은 명령값
        cmd_pose.cmd_vel_linear = self.last_cmd_vel_linear
        cmd_pose.cmd_vel_angular = self.last_cmd_vel_angular

        # /turtle1/pose에서 받은 현재 상태값
        cmd_pose.pose_x = msg.x
        cmd_pose.pose_y = msg.y
        cmd_pose.linear_vel = msg.linear_velocity
        cmd_pose.angular_vel = msg.angular_velocity

        print(f"[cmd_vel] linear={cmd_pose.cmd_vel_linear:.2f}, angular={cmd_pose.cmd_vel_angular:.2f}, [pose] x={cmd_pose.pose_x:.2f}, y={cmd_pose.pose_y:.2f}, linear_vel[{cmd_pose.linear_vel:.2f}, angular_vel={cmd_pose.angular_vel:.2f}]")

def main(args=None):
    rclpy.init(args=args)

    node1 = MsgSubber2()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()