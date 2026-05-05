# 커스텀 메시지 타입의 토픽 2개 구독하기
# pose, cmd_vel 두 개 받기
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from interface_pkg1.msg import MyMessage2

class MsgSubber3(Node):
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
        
        self.timer_period = 1.0
        self.timer = self.create_timer(
            self.timer_period,
            self.timer_callback
        )

        # 커스텀 메시지 객체를 하나 만들어두고 계속 갱신
        self.cmd_pose = MyMessage2()

        #######################         
        # float32 cmd_vel_linear
        # float32 cmd_vel_angular

        # float32 pose_x
        # float32 pose_y
        # float32 pose_theta

        # float32 actual_linear_vel
        # float32 actual_angular_vel
        #######################
        self.cmd_pose.cmd_vel_linear = 0.0
        self.cmd_pose.cmd_vel_angular = 0.0
        self.cmd_pose.pose_x, self.cmd_pose.pose_y, self.cmd_pose.pose_theta = 0.0, 0.0, 0.0
        self.cmd_pose.actual_linear_vel = 0.0
        self.cmd_pose.actual_angular_vel = 0.0

    # 가라고 명령한 값
    def cmd_vel_callback(self, msg):
        self.cmd_pose.cmd_vel_linear = msg.linear.x
        self.cmd_pose.cmd_vel_angular = msg.angular.z
    
    # 현재 이동한 위치 값
    def pose_callback(self, msg):
        # /turtle1/pose에서 받은 현재 상태값
        self.cmd_pose.pose_x = msg.x
        self.cmd_pose.pose_y = msg.y
        self.cmd_pose.pose_theta = msg.theta
        self.cmd_pose.actual_linear_vel = msg.linear_velocity
        self.cmd_pose.actual_angular_vel = msg.angular_velocity

    def timer_callback(self):
        print(f"[cmd_vel] "
              f"linear={self.cmd_pose.cmd_vel_linear:.2f}, "
              f"angular={self.cmd_pose.cmd_vel_angular:.2f}, "
              f"[pose] "
              f"x={self.cmd_pose.pose_x:.2f}, y={self.cmd_pose.pose_y:.2f}, theta={self.cmd_pose.pose_theta:.2f}, "
              f"actual_linear[{self.cmd_pose.actual_linear_vel:.2f}, actual_angular={self.cmd_pose.actual_angular_vel:.2f}]"
        )

def main(args=None):
    rclpy.init(args=args)

    node1 = MsgSubber3()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()