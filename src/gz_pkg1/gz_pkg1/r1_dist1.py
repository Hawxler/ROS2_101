# 거리 제어: /odom을 구독하며 robot1을 2m 이동 후 정지
import rclpy
from rclpy.node import Node
import math

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class MoveDist1(Node):
    def __init__(self):
        super().__init__('r1_dist_node1')

        # 목표 이동 거리(m)
        self.target_dist = 2.0

        # 전진 속도(m/s)
        self.linear_speed = 0.5

        # 시작 위치 저장용
        self.start_x = None
        self.start_y = None

        # 현재 위치 저장용
        self.current_x = 0.0
        self.current_y = 0.0

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

        self.get_logger().info("r1_dist1 시작: /odom 기준 목표거리 이동")

    #1. 현제 위치 갱신
    def odom_callback(self, msg):
        # 현재 위치 읽기
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        # 처음 받은 odom 위치를 시작점으로 지정
        if self.start_x is None:
            self.start_x = self.current_x
            self.start_y = self.current_y

            self.get_logger().info(
                f'시작 위치 저장: x={self.start_x:.2f}, y={self.start_y:.2f}'
            )
    
    #2. 이동 거리 계산
    def get_moved_distance(self):
        # 아직 시작점 못 받았으면 0m
        if self.start_x is None or self.start_y is None:
            return 0.0
        
        dx = self.current_x - self.start_x
        dy = self.current_y - self.start_y
        
        return math.sqrt(dx * dx + dx * dy)

    #3. 목표 거리 - 이동 거리 비교 -> 전진/정지
    def timer_callback(self):
        # 아직 odom을 봇받았으면 대기
        if self.start_x is None:
            self.get_logger().info("odom 대기 중...")
            return
        
        # 이동 거리 갱신
        moved_dist = self.get_moved_distance()

        msg = Twist()

        # 목표 거리 도달 전
        if moved_dist < self.target_dist and not self.done:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0

            self.pubber.publish(msg)

            self.get_logger().info(
                f'전진 중: 이동거리={moved_dist:.2f} / 목표={self.target_dist:.2f}'
            )
        
        # 목표 거리 도달
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

            self.pubber.publish(msg)

            if not self.done:
                self.done = True
                self.get_logger().info(
                    f'목표 도달: 최종 이동거리={moved_dist:.2f}m, 로봇 정지'
                )
    
    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.pubber.publish(msg)
        self.get_logger().info('종료 전 로봇 정지')

def main(args=None):
    rclpy.init(args=args)

    node1 = MoveDist1()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info('Ctrl+C 입력됨')
    finally:
        node1.stop_robot()
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()