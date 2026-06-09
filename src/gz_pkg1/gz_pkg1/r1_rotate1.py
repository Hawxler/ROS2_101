# Gazebo robot1을 /odom 기준으로 목표 각도만큼 제자리 회전시키기
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class RobotRotate(Node):
    def __init__(self):
        super().__init__('r1_rotate_node1')

        # 목표 회전 각도 (degree)
        self.target_angle_deg = 90.0

        # 목표 회전 각도(radian)
        self.target_angle = math.radians(self.target_angle_deg)

        # 회전 속도(rad/s)
        self.angular_speed = 0.5

        # 시작 yaw 저장용
        self.start_yaw = None

        # 현재 yaw 저장용
        self.current_yaw = 0.0

        # 목표 도달 여부
        self.done = False

        # /cmd_vel 발행자
        self.pubber = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # /odom 구독자
        self.subber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # 제어 타이머
        self.timer_period = 0.1
        self.timer = self.create_timer(
            self.timer_period,
            self.timer_callback
        )

        self.get_logger().info(
            f'r1_rotate11 시작: 목표 회전각={self.target_angle_deg:.1f}도'
        )

    def quaternion_to_yaw(self, q):
        """
        quaternion(x, y, z, w) -> yaw 각도(rad)로 변환
        """
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        yaw = math.atan2(siny_cosp, cosy_cosp)

        return yaw
    
    def normalize_angle(self, angle):
        """
        각도를 -pi ~ +pi 범위로 정규화함.
        """
        while angle > math.pi:
            angle -= 2.0 * math.pi

        while angle < -math.pi:
            angle += 2.0 * math.pi

        return angle
    
    def odom_callback(self, msg):
        """
        /odom 메시지에서 현재 yaw를 읽는다.
        처음 받은 yaw -> 시작 yaw로 갱신함.
        """
        q = msg.pose.pose.orientation
        self.current_yaw = self.quaternion_to_yaw(q)

        if self.start_yaw is None:
            self.start_yaw = self.current_yaw

            self.get_logger().info(
                f'시작 yaw 저장: {math.degrees(self.start_yaw):.2f}도'
            )
    
    def get_rotated_angle(self):
        """
        시작 yaw와 현재 yaw의 차이를 계산함.
        결과는 절댓값 radian임.
        """
        if self.start_yaw is None:
            return 0.0
        
        diff = self.current_yaw - self.start_yaw
        diff = self.normalize_angle(diff)

        return abs(diff)
    
    def timer_callback(self):
        """
        목표 각도에 도달할 때까지 회전 명령을 발행함.
        목표에 도달하면 정지 명령을 발행함.
        """
        if self.start_yaw is None:
            self.get_logger().info('odom 대기 중...')
            return
        
        rotated_angle = self.get_rotated_angle()

        msg = Twist()

        if rotated_angle < self.target_angle and not self.done:
            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed

            self.pubber.publish(msg)

            self.get_logger().info(
                f'회전 중: 현재={math.degrees(rotated_angle):.2f}도 / '
                f'목표={self.target_angle_deg:.2f}도'
            )
        
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

            self.pubber.publish(msg)

            if not self.done:
                self.done = True
                self.get_logger().info(
                    f'목표 각도 도달: 최종 회전각={math.degrees(rotated_angle)}'
                )
    
    def stop_robot(self):
        """
        노드 종료 전에 로봇 정지 명령을 한 번 발행함.
        """
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.pubber.publish(msg)

        self.get_logger().info('종료 전 로봇 정지 명령 발행')

def main(args=None):
    rclpy.init(args=args)

    node1 = RobotRotate()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info("Ctrl+C 입력됨")
    finally:
        node1.stop_robot()
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()