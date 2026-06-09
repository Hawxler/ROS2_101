#2. PI 제어 : 목표 위치까지의 거리에 비례하는 P 제어에, 과거의 오차 누적값에 비례하는 I 제어를 추가하여, 보다 정확한 제어를 구현

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

class TurtleCon2(Node):
    def __init__(self):
        super().__init__('pi_con_node1')

        #1. 목표 위치, 허용 오차, 비례 상수, 적분 상수, 적분상한 설정
        self.goal_x = 8.0
        self.tolerance = 0.05
        self.kp = 1.0
        self.ki = 0.1
        self.integral_limit = 10.0  # 적분항의 과도한 증가 방지

        #2. pose 변수 초기화, 오차 누적값 초기화
        self.pose = None
        self.error_sum = 0.0

        #3. 구독자, 발행자, 타이머 설정
        # Pose 메시지를 구독하여 현재 위치를 업데이트하는 구독자 설정
        self.subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # Twist 메시지를 발행하여 명령 속도를 보내는 발행자 설정
        self.pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        
        # timer_callback 함수 호출하여 제어 명령 계산 및 발행
        self.dt = 0.05  # 타이머 주기 (초)
        self.timer = self.create_timer(
            self.dt,
            self.timer_callback
        )

        self.get_logger().info("PI 제어 노드가 시작되었습니다.")

    #4. pose를 수신하여 갱신함
    # msg: 구독자에게 토픽을 통해 Pose 타입 메시지 객체가 수신될 때마다 등록된 콜백 함수에게 msg로 전달됨.
    ########[참고]##########################
    # 토픽(topic) = 메시지가 흐르는 통로 이름 (우편함)
    # 메시지(message/msg) = 그 통로를 통해 실제로 전달되는 데이터 객체
    # 콜백 함수 인자 msg = 토픽을 통해 도착한 실제 메시지 객체
    ######################################## 
    def pose_callback(self, msg):
        self.pose = msg

    #5. 목표 위치까지의 거리(diff_x)를 계산하여 명령 속도를 발행
    def timer_callback(self):
        if self.pose is None:
            return
        
        twist = Twist()

        #(1) 현재 거리차(error_x) 저장
        error_x = self.goal_x - self.pose.x

        #(2) 목표 근처면 정지
        if abs(error_x) < self.tolerance:
            twist.linear.x = 0.0
            self.error_sum = 0.0 # 도착후 오차 누적값 초기화

            self.pubber.publish(twist)

            self.get_logger().info(
                f'[목표 도착] 현재 x: {self.pose.x:.2f}, 남은 거리: {error_x:.2f}, 명령 속도: {twist.linear.x:.2f}'
            )
            return
        
        #(3) 오차 누적
        self.error_sum += error_x * self.dt # dt=0.05s

        #(4) 적분항의 과도한 증가 방지(anti-windup)
        if self.error_sum > self.integral_limit:
            self.error_sum = self.integral_limit
        elif self.error_sum < -self.integral_limit:
            self.error_sum = -self.integral_limit
        
        #(5) PI 제어 계산
        p_control = self.kp * error_x
        i_control = self.ki * self.error_sum

        output = p_control + i_control

        #(6) 명령 속도 제한
        max_speed = 2.0
        if output > max_speed:
            output = max_speed
        elif output < -max_speed:
            output = -max_speed

        #(7) Twist 메시지에 명령 속도 설정 및 발행
        twist.linear.x = output
        twist.angular.z = 0.0
        
        # 발행
        self.pubber.publish(twist)

        self.get_logger().info(
            f'x={self.pose.x:.2f}, '
            f'error_x={error_x:.2f}, '
            f'error_sum={self.error_sum:.2f}, '
            f'p={p_control:.2f}, '
            f'i={i_control:.2f}, '
            f'output={output:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleCon2()
    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        pass

    node1.destroy_node()
    rclpy.shutdown()