# PID + parameter
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from rcl_interfaces.msg import SetParametersResult
import math

class TurtleCon4(Node):
    def __init__(self):
        super().__init__('pid_para_node1')

        #1. ROS2 파라미터 설정 (초기값)
        self.declare_parameter('angular_speed', 1.0)  # 각속도 초기값
        self.declare_parameter('tolerance', 0.01)  # 허용 오차 초기값

        #2. 파라미터 값 읽어오기
        self.angular_speed = self.get_parameter('angular_speed').value
        self.tolerance = self.get_parameter('tolerance').value

        #3. 파라미터 동적 재구성을 위한 콜백 등록
        self.add_on_set_parameters_callback(self.para_callback)

        #4. 현재 회전각과 목표 회전각 설정
        self.current_theta = 0.0
        self.target_theta = 0.0  # goal_theta 토픽에서 갱신됨

        #5. turtle1/pose 토픽 구독자 설정
        self.pose_subber = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.pose_callback,
            10
        )

        #6. goal_theta 토픽 구독자 설정
        self.goal_subber = self.create_subscription(
            Float64,
            'goal_theta',  # radian: 유저가 주는 목표값
            self.goal_callback,
            10
        )

        #7. cmd_vel 토픽 발행자 설정
        self.cmd_vel_pubber = self.create_publisher(
            Twist,
            'turtle1/cmd_vel',
            10
        )

        #8. error 토픽 발행자 설정 (계산된 오차를 발행)
        self.error_pubber = self.create_publisher(
            Float64,
            'theta_error',
            10
        )

    def para_callback(self, params):
        for param in params:
            if param.name == 'angular_speed':
                self.angular_speed = param.value
                self.get_logger().info(f"각속도 파라 갱신됨: {self.angular_speed}")
            elif param.name == 'tolerance':
                self.tolerance = param.value
                self.get_logger().info(f"허용 오차 파라 갱신됨: {self.tolerance}")
            
        result = SetParametersResult()
        result.successful = True
        return result
    
    def pose_callback(self, msg):
        self.current_theta = msg.theta
        self.control()

    def goal_callback(self, msg):
        self.target_theta = msg.data
        self.get_logger().info(f"목표 회전각 갱신됨: {self.target_theta:.2f} rad")
    
    def control(self):
        # 목표 회전각과 현재 회전각의 차이 계산(-pi ~ pi 범위로 보정)
        error_theta = self.target_theta - self.current_theta
        error_theta = math.atan2(math.sin(error_theta), math.cos(error_theta))  # -pi ~ pi 범위로 보정 정규화: (예: 240도 1.33rad -> -150도 0.83rad)

        # error_theta 토픽 발행
        error_msg = Float64()
        error_msg.data = error_theta
        self.error_pubber.publish(error_msg)

        twist_msg = Twist()

        # 오차가 허용범위보다 크면 각속도 유지
        if abs(error_theta) > self.tolerance:
            twist_msg.angular.z = self.angular_speed if error_theta > 0 else -self.angular_speed
        else:
            twist_msg.angular.z = 0.0  # 오차가 충분히 작으면 정지
        twist_msg.linear.x = 0.0
        
        # twist_msg 발행
        self.cmd_vel_pubber.publish(twist_msg)

        self.get_logger().info(
            f"현재 각도: {self.current_theta:.2f}, "
            f"목표 각도: {self.target_theta}, "
            f"각도차: {error_theta:.2f}, "
            f"각속도(angular.z): {twist_msg.angular.z:.2f}"
        )

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleCon4()
    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info("사용자가 중단함.")
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
