# PID 제어: P + I + D를 이용하여 turtle1을 목표 x 위치까지 이동시키는 예제
import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

class TurtleCon3(Node):
    def __init__(self):
        super().__init__('pid_con_node1')

        #1. 목표 위치, 허용 오차, 비례 상수, 적분 상수, 미분 상수, 적분상한 설정
        self.goal_x = 8.0
        self.tolerance = 0.05
        self.kp = 1.0
        self.ki = 0.1
        self.kd = 0.2

        #2. pose 변수 초기화, 누적 오차 초기화, 이전 오차 초기화
        self.pose = None
        self.error_sum = 0.0
        self.prev_error = 0.0
        self.integral_limit = 10.0  # 적분항의 과도한 증가 방지
        self.dt = 0.05  # 타이머 주기 (초)

        #3. 구독자, 발행자, 타이머 설정
        self.subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(
            self.dt,
            self.timer_callback
        )

        self.get_logger().info("PID 제어 노드가 시작되었습니다.")

    def pose_callback(self, msg):
        # /turtle1/pose 토픽을 통해 받은 Pose 메시지 객체 저장
        self.pose = msg

    def timer_callback(self):
        if self.pose is None:
            return
        
        twist = Twist()
        
        #(1) P 제어용: 목표 위치까지의 거리 계산
        error_x = self.goal_x - self.pose.x

        #(2) 목표 근처 도달 시 정지
        if abs(error_x) <= self.tolerance:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            self.pubber.publish(twist)
            
            # 도착 후 I, D 제어를 위해 누적 오차와 이전 오차 초기화
            self.error_sum = 0.0
            self.prev_error = 0.0

            self.get_logger().info(f"[도착] x: {self.pose.x:.2f}, error: {error_x:.2f}")
            return
        
        #(3) I 제어용: 오차 누적
        self.error_sum += error_x * self.dt

        # 적분항의 과도한 증가 방지(anti-windup)
        # 적분 한계치 초과 시 적분값을 한계치로 제한함.
        if self.error_sum > self.integral_limit:
            self.error_sum = self.integral_limit
        elif self.error_sum < -self.integral_limit:
            self.error_sum = -self.integral_limit

        #(4) D 제어용: 오차 변화율 계산
        error_rate = (error_x - self.prev_error) / self.dt

        self.prev_error = error_x # 다음 타이머 콜백에서 D 제어 계산을 위해 현재 오차 저장

        #(5) PID 제어량 계산
        p_control = self.kp * error_x
        i_control = self.ki * self.error_sum
        d_control = self.kd * error_rate

        output = p_control + i_control + d_control

        #(6) 명령 속도 제한
        max_speed = 2.0
        if output > max_speed:
            output = max_speed
        elif output < -max_speed:
            output = -max_speed
        
        #(7) Twist 메시지에 명령 속도 설정 및 발행
        twist.linear.x = output
        twist.angular.z = 0.0

        self.pubber.publish(twist)

        self.get_logger().info(
            f'x={self.pose.x:.2f}, '
            f'error_x={error_x:.2f}, '
            f'error_sum={self.error_sum:.2f}, '
            f'p={p_control:.2f}, '
            f'i={i_control:.2f}, '
            f'd={d_control:.2f}, '
            f'output={output:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleCon3()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()